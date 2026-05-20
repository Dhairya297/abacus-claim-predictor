import streamlit as st
import requests
import json

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

API_URL = "http://127.0.0.1:8000/predict-claim"

st.set_page_config(
    page_title="Claim Denial Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background-color: #0d0f14;
        color: #e2e8f0;
    }

    /* ── Header ─────────────────────────────────────────────── */
    .header-block {
        background: linear-gradient(135deg, #0f1923 0%, #1a2535 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .header-block::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4, #3b82f6);
    }
    .header-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.5px;
    }
    .header-sub {
        font-size: 0.9rem;
        color: #64748b;
        margin: 0;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* ── Section labels ──────────────────────────────────────── */
    .section-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: #3b82f6;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1e3a5f;
    }

    /* ── Text inputs & number inputs ─────────────────────────── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #0d1117 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 6px !important;
        color: #e2e8f0 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.8rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    }
    .stTextInput label,
    .stNumberInput label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
    }

    /* ── Selectbox ───────────────────────────────────────────── */
    .stSelectbox > div > div {
        background-color: #0d1117 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 6px !important;
        color: #e2e8f0 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.85rem !important;
        min-height: 2.4rem !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    }
    .stSelectbox label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        margin-bottom: 0.3rem !important;
    }
    [data-baseweb="popover"] ul {
        background-color: #0d1117 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 6px !important;
    }
    [data-baseweb="popover"] li {
        background-color: #0d1117 !important;
        color: #e2e8f0 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.85rem !important;
    }
    [data-baseweb="popover"] li:hover {
        background-color: #1e3a5f !important;
        color: #60a5fa !important;
    }

    /* ── Select Slider ───────────────────────────────────────── */
    .stSlider label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
    }
    .stSlider [data-baseweb="slider"] {
        margin-top: 0.8rem !important;
        margin-bottom: 0.4rem !important;
    }
    .stSlider [data-baseweb="slider"] > div > div:first-child {
        background: #1f2937 !important;
        height: 4px !important;
        border-radius: 2px !important;
    }
    .stSlider [data-baseweb="slider"] > div > div:nth-child(2) {
        background: linear-gradient(90deg, #1d4ed8, #3b82f6) !important;
        height: 4px !important;
        border-radius: 2px !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #3b82f6 !important;
        border: 2px solid #1d4ed8 !important;
        width: 16px !important;
        height: 16px !important;
        border-radius: 50% !important;
        box-shadow: 0 0 6px rgba(59,130,246,0.5) !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"]:hover {
        background: #60a5fa !important;
        box-shadow: 0 0 10px rgba(59,130,246,0.7) !important;
    }
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #475569 !important;
        font-size: 0.7rem !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    .stSlider [data-baseweb="tooltip"] {
        background: #1e3a5f !important;
        color: #60a5fa !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.75rem !important;
        border-radius: 4px !important;
        padding: 0.2rem 0.5rem !important;
    }

    /* ── Button ──────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 2rem !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        margin-top: 0.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    }

    /* ── Risk badge ──────────────────────────────────────────── */
    .risk-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .risk-high   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3);  }
    .risk-medium { background: rgba(234,179,8,0.15);  color: #fbbf24; border: 1px solid rgba(234,179,8,0.3);  }
    .risk-low    { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3);  }

    /* ── Score card ──────────────────────────────────────────── */
    .score-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-value {
        font-family: 'Montserrat', sans-serif;
        font-size: 3rem;
        font-weight: 600;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    .score-label {
        font-size: 0.75rem;
        color: #64748b;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ── Prediction card ─────────────────────────────────────── */
    .prediction-card {
        background: #111827;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .prediction-denied   { border: 1px solid rgba(239,68,68,0.4); }
    .prediction-approved { border: 1px solid rgba(34,197,94,0.4); }
    .prediction-text {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .text-denied   { color: #f87171; }
    .text-approved { color: #4ade80; }
    .text-medium   { color: #fbbf24; }

    /* ── Reason card ─────────────────────────────────────────── */
    .reason-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-left: 3px solid #3b82f6;
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .reason-text {
        color: #cbd5e1;
        font-size: 0.85rem;
        margin: 0 0 0.4rem 0;
    }

    /* ── Recommendation card ─────────────────────────────────── */
    .rec-card {
        background: linear-gradient(135deg, #0f1f3d, #0f172a);
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 0.8rem;
    }
    .rec-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        color: #3b82f6;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .rec-text {
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.7;
    }

    /* ── Error box ───────────────────────────────────────────── */
    .error-box {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #f87171;
        font-size: 0.85rem;
        font-family: 'Montserrat', sans-serif;
    }

    /* ── Hide Streamlit chrome ───────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def call_api(payload: dict) -> dict:
    """POST to FastAPI and return JSON response."""
    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Make sure FastAPI is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The AI pipeline took too long to respond."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"API error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_score_color(risk_score: float) -> str:
    if risk_score >= 70:
        return "#f87171"
    elif risk_score >= 40:
        return "#fbbf24"
    return "#4ade80"


def get_risk_class(risk_level: str) -> str:
    mapping = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}
    return mapping.get(risk_level.upper(), "risk-medium")


def get_prediction_class(prediction: str) -> str:
    if "DENIED" in prediction.upper():
        return "prediction-denied", "text-denied"
    return "prediction-approved", "text-approved"


def render_threshold_bar(label: str, value: float, color: str):
    pct = min(value * 100, 100)
    st.markdown(f"""
    <div class="threshold-row">
        <span class="threshold-label">{label}</span>
        <div class="threshold-bar-bg">
            <div class="threshold-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
        <span class="threshold-value">{value:.1%}</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="header-block">
    <p class="header-title">🏥 Claim Denial Predictor</p>
    <p class="header-sub">AI-POWERED HEALTHCARE CLAIMS DENIAL SYSTEM </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────

left_col, right_col = st.columns([1, 1.6], gap="large")


# ─────────────────────────────────────────────
# LEFT — INPUT FORM
# ─────────────────────────────────────────────
with left_col:
    st.markdown('<p class="section-label">Claim Input</p>', unsafe_allow_html=True)

    with st.form("claim_form", clear_on_submit=False):

        claim_id = st.text_input(
            "Claim ID",
            value="CLM1001",
            placeholder="e.g. CLM1001"
        )
        provider_id = st.selectbox(
            "Provider ID",
            options=[f"PR{i}" for i in range(100, 121)],
            index=1  # defaults to PR101
        )
        diagnosis_code = st.selectbox(
            "Diagnosis Code (ICD-10)",
            options=["D10", "D20", "D30", "D40", "D50", "D60"],
            index=0
        )
        procedure_code = st.selectbox(
            "Procedure Code (CPT)",
            options=["PROC1", "PROC2", "PROC3", "PROC4", "PROC5", "PROC6"],
            index=0
        )
        billed_amount = st.number_input(
            "Billed Amount ($)",
            min_value=0.0,
            value=12000.0,
            step=100.0,
            format="%.2f"
        )
        date = st.text_input(
            "Date of Service",
            value="2026-05-15",
            placeholder="YYYY-MM-DD"
        )

        submitted = st.form_submit_button("⚡ CHECK CLAIM")
            
    # API status indicator
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">API Status</p>', unsafe_allow_html=True)
    try:
        r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 1rem;
                    background:#0f1f0f;border:1px solid #166534;border-radius:6px;">
            <span style="color:#4ade80;font-size:0.75rem;">●</span>
            <span style="font-family:'Montserrat',monospace;font-size:0.72rem;color:#4ade80;">
                FASTAPI ONLINE · port 8000
            </span>
        </div>""", unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 1rem;
                    background:#1f0f0f;border:1px solid #7f1d1d;border-radius:6px;">
            <span style="color:#f87171;font-size:0.75rem;">●</span>
            <span style="font-family:'Montserrat',monospace;font-size:0.72rem;color:#f87171;">
                FASTAPI OFFLINE · start uvicorn
            </span>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RIGHT — OUTPUT
# ─────────────────────────────────────────────

with right_col:
    st.markdown('<p class="section-label">Results</p>', unsafe_allow_html=True)

    if not submitted:
        st.markdown("""
        <div style="background:#111827;border:1px dashed #1f2937;border-radius:10px;
                    padding:3rem;text-align:center;margin-top:1rem;">
            <p style="font-family:'Montserrat',monospace;font-size:0.8rem;
                      color:#374151;letter-spacing:1px;">
                AWAITING CLAIM SUBMISSION
            </p>
            <p style="font-size:0.75rem;color:#1f2937;margin-top:0.5rem;">
                Fill in the form and click CHECK CLAIM
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Validate inputs
        errors = []
        if not claim_id.strip():
            errors.append("Claim ID is required.")
        if not provider_id.strip():
            
            errors.append("Provider ID is required.")
        if not diagnosis_code.strip():
            errors.append("Diagnosis Code is required.")
        if not procedure_code.strip():
            errors.append("Procedure Code is required.")
        if billed_amount <= 0:
            errors.append("Billed amount must be greater than 0.")
        if not date.strip():
            errors.append("Date is required.")

        if errors:
            for err in errors:
                st.markdown(f'<div class="error-box">⚠ {err}</div>', unsafe_allow_html=True)
        else:
            payload = {
                "claim_id":       claim_id.strip(),
                "provider_id":    provider_id.strip(),
                "diagnosis_code": diagnosis_code.strip(),
                "procedure_code": procedure_code.strip(),
                "billed_amount":  float(billed_amount),
                "date":           date.strip()
            }

            with st.spinner("Running AI pipeline..."):
                result = call_api(payload)

            if not result["success"]:
                st.markdown(
                    f'<div class="error-box">⚠ {result["error"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                data = result["data"]
                risk_level  = data.get("risk_level", "LOW").upper()
                is_approved = risk_level == "LOW"

                # ── Row 1: Prediction + Risk Score ──────────────────────────────
                c1, c2 = st.columns(2)

                with c1:
                    card_cls, text_cls = get_prediction_class(data["prediction"])
                    st.markdown(f"""
                    <div class="prediction-card {card_cls}">
                        <div class="score-label" style="margin-bottom:0.5rem;">VERDICT</div>
                        <div class="prediction-text {text_cls}" style="margin-bottom:0.5rem;">{data["prediction"]}</div>
                        <br>
                        <span class="risk-badge {get_risk_class(risk_level)}">
                            {risk_level}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    score_color = get_score_color(data["risk_score"])
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">RISK SCORE</div>
                        <div class="score-value" style="color:{score_color};">
                            {data["risk_score"]:.1f}<span style="font-size:1.2rem;color:#64748b;">%</span>
                        </div>
                        <div class="score-label">DENIAL PROBABILITY</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── APPROVED → stop here ─────────────────────────────────────────
                if is_approved:
                    st.markdown("""
                    <div style="background:#0f1f0f;border:1px solid #166534;border-radius:10px;
                                padding:1.5rem;text-align:center;margin-top:1rem;">
                        <p style="color:#4ade80;font-family:'IBM Plex Mono',monospace;
                                font-size:0.9rem;margin:0;letter-spacing:1px;">
                                CLAIM APPROVED
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # ── DENIED / MEDIUM → show full detail ──────────────────────────
                else:
                    # Reasons
                    st.markdown('<p class="section-label" style="margin-top:1rem;">DENIAL REASONS</p>', unsafe_allow_html=True)
                    for i, reason in enumerate(data.get("top_reasons", []), 1):
                        shap_val  = reason.get("shap_value", 0)
                        feat_val  = reason.get("feature_value", "")
                        feat_display = f"{feat_val:.3f}" if isinstance(feat_val, float) else str(feat_val)
                        st.markdown(f"""
                        <div class="reason-card">
                            <p class="reason-text"><b style="color:#93c5fd;">#{i}</b> &nbsp;{reason["business_reason"]}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Policy — LLM summary only, no raw chunks
                    policy_summary = data.get("policy_summary")

                    if isinstance(policy_summary, list):
                        policy_summary = "\n".join(policy_summary)

                    # Handle case where LLM writes "1. text 2. text" on one line without newlines
                    if isinstance(policy_summary, str) and "\n" not in policy_summary:
                        import re
                        policy_summary = re.sub(r'\s+(\d+\.)', r'\n\1', policy_summary).strip()

                    if policy_summary:
                        st.markdown('<p class="section-label" style="margin-top:1rem;">Policy - Rules and Regulations</p>', unsafe_allow_html=True)

                        lines_html = "".join(
                            f'<div style="margin-bottom:0.6rem;color:#cbd5e1;font-size:0.85rem;line-height:1.6;">'
                            f'{line.strip()}'
                            f'</div>'
                            for line in policy_summary.split("\n")
                            if line.strip()
                        )
                        st.markdown(f"""
                        <div class="rec-card">
                            <div class="rec-label">POLICY SUMMARY</div>
                            <div class="rec-text">{lines_html}</div>
                        </div>
                        """, unsafe_allow_html=True)


                    # Recommendation
                    recommendations = data.get("recommendations", [])
                    next_action = data.get("next_action", "")

                    if recommendations:
                        st.markdown('<p class="section-label" style="margin-top:1rem;">RECOMMENDATIONS</p>', 
                                    unsafe_allow_html=True)
                        for rec in recommendations:
                            st.markdown(f"""
                            <div class="rec-card">
                                <div class="rec-label">FOR: {rec.get("reason", "")[:60]}...</div>
                                <div class="rec-text">{rec.get("action", "")}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    if next_action:
                        st.markdown(f"""
                        <div class="rec-card" style="border-color:#f59e0b;background:linear-gradient(135deg,#1c1200,#0f172a);">
                            <div class="rec-label" style="color:#f59e0b;">⚡ IMMEDIATE NEXT ACTION</div>
                            <div class="rec-text">{next_action}</div>
                        </div>
                        """, unsafe_allow_html=True)


                    # Raw JSON debug
                    with st.expander("Raw API Response", expanded=False):
                        st.json(data)