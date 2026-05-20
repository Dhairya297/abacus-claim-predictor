# recommendation_service.py

from agents.recommendation_agent import RecommendationAgent
from utils.logger import logger

class RecommendationService:

    def __init__(self):
        self.agent = RecommendationAgent()
        
    def generate_recommendation(
        self,
        prediction,
        risk_score,
        top_reasons,
        retrieved_policies
    ):

        try:
            logger.info("Generating AI recommendations.")

            recommendation_response = (
                self.agent
                .generate_recommendation(
                    prediction=prediction,
                    risk_score=risk_score,
                    top_reasons=top_reasons,
                    retrieved_policies=(retrieved_policies)
                )
            )

            logger.info("Recommendation generation completed.")
            return recommendation_response

        except Exception as e:
            logger.exception("Recommendation service failed.")
            raise e