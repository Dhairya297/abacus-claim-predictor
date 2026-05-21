import json
import re
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from utils.logger import logger
from config.error_codes import ErrorCode

class RecommendationAgent:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_recommendation(
        self,
        prediction,
        risk_score,
        top_reasons,
        retrieved_policies
    ):
        try:
            reasons_text = "\n".join([
                f"- {r['business_reason']}"
                for r in top_reasons
            ])

            policy_text = "\n\n".join([
                f"[POLICY DOCUMENT {i+1}]\n"
                f"Section: {p.get('section_title', 'Unknown Section')}\n"
                f"Source: {p.get('source_file', 'Unknown Source')}\n"
                f"Content:\n{p.get('policy_text', '')}"
                for i, p in enumerate(retrieved_policies)
            ])

            prompt = f"""
                You are a healthcare claims adjudication expert reviewing a denied insurance claim.

                CLAIM EVALUATION:
                - Prediction: {prediction}
                - Risk Score: {risk_score}%

                TOP DENIAL REASONS (from ML model):
                {reasons_text}

                RETRIEVED POLICY DOCUMENTS:
                {policy_text}

                Your task is to analyze the policy documents carefully and extract every relevant rule,
                regulation, code reference, and requirement that applies to this claim.

                Respond ONLY with a JSON object containing exactly these 3 fields:

                # Change the policy_summary instruction in prompt to:

                1. "policy_summary": A plain string with exactly 3-5 numbered points.
                You MUST put a newline character \n between each point.
                Each point is one sentence about ONE specific rule or regulation.
                
                The string must look exactly like this:
                "1. First rule here.\n2. Second rule here.\n3. Third rule here."
                ALWAYS FOLLOW THIS FORMAT
                
                NEVER write all points on a single line.
                NEVER use the literal characters backslash-n — use actual line breaks in the string.
                send the response such that the line must be changed after each and every bullet point. make sure you follow this format of changing lines.
                Each point must be one detailed point/sentence about ONE specific rule, code, or regulation.
                Extract actual rules, codes, thresholds, and timeframes from the policy documents.
                Never combine multiple rules into one point. If there are any codes or rules or regulations, make sure you mention them.

                2. "recommendations": A JSON array with one object per denial reason listed above. Each object must have:
                - "reason": copy the denial reason text exactly as listed above
                - "action": one specific, actionable sentence telling the provider exactly what to do

                3. "next_action": A single string — the single most urgent thing the provider must do immediately,
                referencing a specific policy rule or deadline if available.

                RULES:
                - policy_summary MUST be a JSON array of strings, never a plain string.
                - next_action MUST be a plain string, never an array.
                - Do not use markdown, bullet symbols (•, -, *), or code fences anywhere in the JSON values.
                - Do not include any text outside the JSON object.

                Respond ONLY with valid JSON in exactly this shape:
                {{
                "policy_summary": [
                    "Rule or regulation extracted from policy doc 1...",
                    "Rule or regulation extracted from policy doc 2...",
                    "Rule or regulation extracted from policy doc 3..."
                ],
                "recommendations": [
                    {{"reason": "exact denial reason text", "action": "specific action for provider"}}
                ],
                "next_action": "Most urgent action with specific deadline or rule reference."
                }}
                """

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            raw = response.choices[0].message.content.strip()

            # Strip markdown fences if present
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"^```\s*",     "", raw)
            raw = re.sub(r"\s*```$",     "", raw)
            raw = raw.strip()

            try:
                result = json.loads(raw)

                # Guard: if LLM still returns a list for policy_summary, join it into a string
                if isinstance(result.get("policy_summary"), list):
                    result["policy_summary"] = " ".join(result["policy_summary"])

                # Guard: if recommendations came back as a string blob, wrap it
                if isinstance(result.get("recommendations"), str):
                    result["recommendations"] = [{"reason": "General", "action": result["recommendations"]}]
    
                # Guard: if next_action is missing
                if not result.get("next_action"):
                    result["next_action"] = "Review claim manually with a senior adjudicator."
            except json.JSONDecodeError:
                result = {
                    "policy_summary":   "Policy context could not be summarized.",
                    "recommendations":  [{"reason": r["business_reason"], "action": "Review manually."} 
                                        for r in top_reasons],
                    "next_action":      "Review claim manually with a senior adjudicator."
                }

            return result

        except Exception as e:
            logger.exception("Recommendation generation failed.")
            raise RuntimeError(ErrorCode.PREDICTION_ERROR) from e