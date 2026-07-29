"""
CareerPilot AI — app.py
========================
Entry point. Run with:  streamlit run app.py

Seven-page flow controlled entirely via st.session_state["page"]:
  1. landing         5. interview
  2. upload_resume   6. jobs
  3. job_description 7. toolkit (outreach email / learning roadmap / report)
  4. results

All heavy imports (spaCy, sentence-transformers) happen inside modules/
and are cached with @st.cache_resource, so they only load once per session.
"""

import re
import streamlit as st
from dotenv import load_dotenv
import base64

from modules.resume_parser import extract_text_from_pdf, extract_text_from_docx, extract_skills, extract_layout_lines
from modules.matcher import compute_match
from modules.interview import (
    generate_interview, evaluate_answers,
    generate_mock_interview_questions, evaluate_mock_interview,
)
from modules.job_recommender import recommend_jobs, ELIGIBILITY_THRESHOLD
from modules.jd_input import extract_jd_from_url, generate_sample_jd, fetch_company_context
from modules.career_tools import (
    generate_outreach_email, generate_learning_roadmap,
    build_report_markdown, generate_bullet_rewrites,
    generate_tailored_resume, build_resume_pdf, build_resume_docx,
    build_resume_diff_html, build_section_diffs, generate_layout_constrained_rewrites,
    apply_layout_preserving_edits, lines_to_text, generate_resume_debate,
)
from modules.career_readiness import (
    generate_7day_learning_plan, generate_ai_mini_project,
    generate_improvement_summary, recommend_skill_based_jobs,
)

load_dotenv()

st.set_page_config(page_title="CareerPilot AI", page_icon="🧭", layout="wide")

# ============================================================================
# PREMIUM SAAS CSS — Modern, Clean, Professional
# ============================================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }
#MainMenu, header, footer, .stDeployButton, .stStatusWidget,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"], section[data-testid="stSidebar"] > div:first-child > div:first-child {
    display: none !important;
}
.stApp { background: #F8FAFC; min-height: 100vh; }
.stApp::before {
    content: ''; position: fixed; top: -20%; right: -10%;
    width: 60vw; height: 60vw;
    background: radial-gradient(circle, rgba(37,99,235,0.08), transparent 70%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.stApp::after {
    content: ''; position: fixed; bottom: -20%; left: -10%;
    width: 50vw; height: 50vw;
    background: radial-gradient(circle, rgba(139,92,246,0.07), transparent 70%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.stApp > div:first-child { position: relative; z-index: 1; }
.block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
.cp-navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 0; margin-bottom: 2rem;
}
.cp-nav-logo { display: flex; align-items: center; gap: 0.6rem; font-size: 1.25rem; font-weight: 800; color: #111827; text-decoration: none; }
.cp-nav-logo span { color: #2563EB; }
.cp-nav-links { display: flex; align-items: center; gap: 1.75rem; }
.cp-nav-links a { color: #6B7280; font-size: 0.9rem; font-weight: 500; text-decoration: none; transition: color 0.2s; cursor: pointer; }
.cp-nav-links a:hover { color: #2563EB; }
.cp-nav-actions { display: flex; align-items: center; gap: 0.75rem; }
.cp-nav-btn {
    padding: 0.5rem 1.25rem; border-radius: 999px; font-size: 0.875rem;
    font-weight: 600; cursor: pointer; transition: all 0.2s;
    border: 1.5px solid #E5E7EB; background: transparent; color: #374151;
}
.cp-nav-btn:hover { background: #EEF4FF; border-color: #2563EB; color: #2563EB; }
.cp-nav-btn-primary { background: #2563EB; color: #fff !important; border-color: #2563EB; box-shadow: 0 1px 3px rgba(37,99,235,0.3); }
.cp-nav-btn-primary:hover { background: #1D4ED8; border-color: #1D4ED8; }
.cp-card {
    background: #FFFFFF; border-radius: 20px; padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem; border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: box-shadow 0.25s ease, transform 0.2s ease;
}
.cp-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.04); }
.cp-card-glass { background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); }
div.stButton > button, div.stDownloadButton > button {
    height: 48px; border-radius: 999px; font-weight: 600;
    font-size: 0.9rem; padding: 0 1.75rem; transition: all 0.2s ease; border: 1.5px solid #E5E7EB;
}
div.stButton > button[kind="primary"], div.stDownloadButton > button,
button[data-testid*="baseButton-primary"] {
    background: #2563EB !important; border-color: #2563EB !important;
    color: #FFFFFF !important; box-shadow: 0 1px 3px rgba(37,99,235,0.3) !important;
}
div.stButton > button[kind="primary"] *,
div.stDownloadButton > button *,
button[data-testid*="baseButton-primary"] * {
    color: #FFFFFF !important;
}
div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover,
button[data-testid*="baseButton-primary"]:hover {
    background: #1D4ED8 !important; border-color: #1D4ED8 !important;
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
}
div.stButton > button[kind="secondary"] { background: #FFFFFF !important; border-color: #E5E7EB !important; color: #374151 !important; }
div.stButton > button[kind="secondary"]:hover { background: #EEF4FF !important; border-color: #2563EB !important; color: #2563EB !important; }
div.stButton > button:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
h1, h2, h3, h4, h5, h6 { color: #111827; font-weight: 700; letter-spacing: -0.02em; }
h1 { font-size: 2.4rem; line-height: 1.2; }
h2 { font-size: 1.75rem; }
h3 { font-size: 1.35rem; }
p, li, .stCaption, label, span { color: #6B7280; }
.stCaption { font-size: 0.8rem; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea,
.stSelectbox > div > div > div, .stMultiSelect > div > div > div {
    border-radius: 12px !important; border: 1.5px solid #E5E7EB !important;
    padding: 0.75rem 1rem !important; font-size: 0.9rem !important;
    background: #FFFFFF !important; transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color: #2563EB !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stTextInput > div > div > input:hover, .stTextArea > div > div > textarea:hover { border-color: #93C5FD !important; }
[data-testid="stFileUploader"] {
    border-radius: 16px !important; border: 2px dashed #E5E7EB !important;
    background: #F8FAFC !important; padding: 2rem !important; transition: all 0.25s !important;
    backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
    text-shadow: none !important; isolation: isolate !important;
}
[data-testid="stFileUploader"]:hover { border-color: #2563EB !important; background: #EEF4FF !important; }
[data-testid="stFileUploader"] > section > div:first-child { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stFileUploader"] * { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; text-shadow: none !important; }
[data-testid="stFileUploader"] label { display: none !important; }
.stProgress > div > div > div { border-radius: 999px !important; height: 8px !important; background-image: none !important; }
.stProgress > div > div { background: #E5E7EB !important; border-radius: 999px !important; overflow: hidden; }
.cp-badge { display: inline-block; padding: 0.3rem 0.85rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; margin: 0.2rem 0.3rem 0.2rem 0; transition: transform 0.15s; }
.cp-badge:hover { transform: translateY(-1px); }
.cp-badge-good { background: #D1FAE5; color: #065F46; }
.cp-badge-bad { background: #FEE2E2; color: #991B1B; }
.cp-badge-warn { background: #FEF3C7; color: #92400E; }
.cp-badge-info { background: #DBEAFE; color: #1E40AF; }
.cp-badge-purple { background: #EDE9FE; color: #5B21B6; }
.cp-score-label { color: #6B7280; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.cp-status-good { background: #D1FAE5; border: 1px solid #A7F3D0; border-radius: 12px; padding: 1rem 1.25rem; color: #065F46; font-weight: 600; margin-bottom: 1rem; }
.cp-status-bad { background: #FEE2E2; border: 1px solid #FECACA; border-radius: 12px; padding: 1rem 1.25rem; color: #991B1B; font-weight: 600; margin-bottom: 1rem; }
.cp-status-warn { background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 12px; padding: 1rem 1.25rem; color: #92400E; font-weight: 600; margin-bottom: 1rem; }
.cp-step-track { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; }
.cp-step { flex: 1; height: 4px; border-radius: 2px; background: #E5E7EB; transition: background 0.3s; }
.cp-step.cp-step-done { background: #2563EB; }
.cp-step-label { color: #2563EB; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
.cp-circular-wrapper { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.cp-compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }
.cp-compare-original { background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 1.25rem; }
.cp-compare-optimized { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 12px; padding: 1.25rem; }
.cp-compare-label { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }
.cp-compare-original .cp-compare-label { color: #DC2626; }
.cp-compare-optimized .cp-compare-label { color: #16A34A; }
.cp-metric { text-align: center; padding: 0.5rem; }
.cp-metric-value { font-size: 1.75rem; font-weight: 800; color: #111827; }
.cp-metric-label { font-size: 0.75rem; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
hr { margin: 1.5rem 0; border-color: #E5E7EB; border-width: 0; border-top: 1px solid #E5E7EB; }
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid #E5E7EB; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; padding: 0.5rem 1rem !important; font-weight: 500; font-size: 0.85rem; color: #6B7280 !important; transition: all 0.2s; }
.stTabs [aria-selected="true"] { color: #2563EB !important; font-weight: 600 !important; }
div[role="radiogroup"] { display: flex; gap: 0.5rem; flex-wrap: wrap; }
div[role="radiogroup"] label { border: 1.5px solid #E5E7EB; border-radius: 999px; padding: 0.5rem 1.25rem; font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.2s; background: #FFFFFF; }
div[role="radiogroup"] label:hover { border-color: #93C5FD; background: #EEF4FF; }
div[role="radiogroup"] label[data-checked="true"] { border-color: #2563EB; background: #2563EB; color: #fff !important; }
.streamlit-expanderHeader { font-weight: 600; font-size: 0.9rem; color: #111827 !important; border-radius: 12px; background: #F8FAFC; padding: 0.75rem 1rem; }
.streamlit-expanderContent { border: 1px solid #E5E7EB; border-radius: 0 0 12px 12px; padding: 1rem; }
section[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E5E7EB; padding-top: 1rem; }
section[data-testid="stSidebar"] > div:first-child { padding: 1rem 0.75rem; }
section[data-testid="stSidebar"] .stButton button {
    border-radius: 10px; padding: 0.6rem 1rem; font-size: 0.85rem;
    border: none; background: transparent; color: #6B7280; font-weight: 500;
    text-align: left; justify-content: flex-start; width: 100%; transition: all 0.15s;
}
section[data-testid="stSidebar"] .stButton button:hover { background: #EEF4FF; color: #2563EB; }
section[data-testid="stSidebar"] hr { margin: 0.75rem 0; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
.cp-animate-in { animation: fadeInUp 0.5s ease forwards; }
.cp-animate-in-left { animation: slideInLeft 0.5s ease forwards; }
.cp-animate-in-right { animation: slideInRight 0.5s ease forwards; }
@media (max-width: 768px) {
    .cp-nav-links { display: none; }
    .cp-compare-grid { grid-template-columns: 1fr; }
    h1 { font-size: 1.75rem; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    [data-testid="column"] { min-width: 100% !important; }
}
.cp-success-gradient {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 1px solid #6EE7B7;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.25rem;
}
.cp-mentor-card {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border: 1px solid #93C5FD;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.25rem;
}
.cp-decision-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 1.75rem;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.25s ease;
    text-align: center;
    height: 100%;
}
.cp-decision-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.06), 0 12px 32px rgba(0,0,0,0.04);
}
.cp-icon-circle {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-size: 1.5rem;
}
.cp-progress-dashboard {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid #E5E7EB;
    margin-bottom: 1.25rem;
}
.cp-diff-positive { color: #059669; font-weight: 600; }
.cp-diff-negative { color: #DC2626; font-weight: 600; }
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

STEP_SEQUENCE = ["upload_resume", "job_description", "results", "resume_optimize"]
STEP_LABELS = {
    "upload_resume": "Upload Resume",
    "job_description": "Job Description",
    "results": "Resume Match Score",
    "resume_optimize": "Optimize & Compare",
}


def render_top_navbar():
    """Render the premium top navigation bar."""
    st.markdown("""
    <nav class="cp-navbar">
        <a class="cp-nav-logo" href="#">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="#2563EB"/>
                <circle cx="16" cy="16" r="8" fill="white" opacity="0.9"/>
                <path d="M16 10 L20 16 L16 22 L12 16 Z" fill="#2563EB"/>
            </svg>
            Career<span>Pilot</span>
        </a>
        <div class="cp-nav-links">
            <a href="#" onclick="return false;">Home</a>
            <a href="#" onclick="return false;">Features</a>
            <a href="#" onclick="return false;">Dashboard</a>
            <a href="#" onclick="return false;">Roadmap</a>
            <a href="#" onclick="return false;">Interview</a>
        </div>
        <div class="cp-nav-actions">
            <button class="cp-nav-btn">Login</button>
            <button class="cp-nav-btn cp-nav-btn-primary">Get Started</button>
        </div>
    </nav>
    """, unsafe_allow_html=True)


def render_step_track(current_page: str):
    if current_page not in STEP_SEQUENCE:
        return
    idx = STEP_SEQUENCE.index(current_page)
    bars = "".join(
        f'<div class="cp-step {"cp-step-done" if i <= idx else ""}"></div>' for i in range(len(STEP_SEQUENCE))
    )
    st.markdown(f'<div class="cp-step-label">Step {idx + 1} of {len(STEP_SEQUENCE)} &middot; {STEP_LABELS[current_page]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cp-step-track">{bars}</div>', unsafe_allow_html=True)


def circular_score(score: float, label: str = "", size: str = "150px") -> str:
    """Circular score gauge with color coding: green >80, orange 60-80, red <60."""
    deg = max(0, min(100, score)) * 3.6
    inner_size = f"calc({size} - 32px)"
    font_size = "2rem" if "150" in size else "1.5rem"
    if score >= 80:
        ring_color = "#10B981"
    elif score >= 60:
        ring_color = "#F59E0B"
    else:
        ring_color = "#EF4444"
    return f"""
    <div class="cp-circular-wrapper">
      <div style="width:{size};height:{size};border-radius:50%;
          background:conic-gradient({ring_color} {deg}deg, #E5E7EB 0deg);
          display:flex;align-items:center;justify-content:center;
          transition:all 0.5s ease;">
        <div style="width:{inner_size};height:{inner_size};border-radius:50%;background:#fff;
            display:flex;align-items:center;justify-content:center;
            font-size:{font_size};font-weight:800;color:#111827;">
          {score}%
        </div>
      </div>
      <div class="cp-score-label">{label}</div>
    </div>
    """


# ----------------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------------
DEFAULT_STATE = {
    "page": "landing",
    "resume_text": None,
    "resume_skills": [],
    "resume_file_type": None,
    "jd_text": "",
    "match_result": None,
    "interview": None,
    "interview_answers": {},
    "evaluation": None,
    "recommended_jobs": None,
    "outreach_email": None,
    "learning_roadmap": None,
    "bullet_rewrites": None,
    "tailored_resume": None,
    "resume_diff_html": None,
    "section_diffs": None,
    "resume_pdf_bytes": None,
    "resume_layout_lines": None,
    "layout_rewrites": None,
    "optimized_pdf_bytes": None,
    "optimized_resume_text": None,
    "recalculated_match": None,
    "resume_debate": None,
    "mock_interview_questions": None,
    "mock_interview_answers": {},
    "mock_interview_evaluation": None,
    "company_name": "",
    "company_url": "",
    "company_context": "",
    # Career Readiness Decision Engine state
    "career_readiness_shown": False,
    "learning_plan_7day": None,
    "ai_mini_project": None,
    "improved_resume_text": None,
    "improved_resume_score": None,
    "improvement_summary": None,
    "career_readiness_jobs": None,
    "progress_history": [],
    "previous_resume_skills": [],
    "career_readiness_origin": None,
}
for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def goto(page: str):
    st.session_state["page"] = page
    st.rerun()


def reset_all():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value
    st.rerun()


# ============================================================================
# Page 1 — Landing Page (Premium SaaS Hero)
# ============================================================================
def page_landing():
    render_top_navbar()
    hero_col1, hero_col2 = st.columns([1.1, 1])
    
    with hero_col1:
        st.markdown("<span class='cp-animate-in' style='display:inline-block;background:#EEF4FF;color:#2563EB;padding:0.35rem 0.9rem;border-radius:999px;font-size:0.8rem;font-weight:600;margin-bottom:1.25rem;'>AI Resume Analyzer</span>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:2.8rem;line-height:1.15;margin-bottom:1rem;' class='cp-animate-in'>Is your resume ready for<br>your <span style='color:#2563EB;'>dream job</span>?</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p style='font-size:1.05rem;color:#6B7280;line-height:1.6;margin-bottom:1.5rem;' class='cp-animate-in'>
        Check ATS compatibility, semantic matching, missing skills, interview readiness, 
        personalized quizzes, and AI roadmap generation — all in one place.
        </p>
        """, unsafe_allow_html=True)
        
        # Premium Upload Card
        st.markdown("""
        <div class='cp-card cp-card-glass' style='border-radius:24px;text-align:center;padding:2rem;margin-bottom:0.5rem;'>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.5" style="margin-bottom:0.75rem;">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p style='font-weight:600;color:#111827;font-size:1rem;margin-bottom:0.5rem;'>Upload your resume to get started</p>
            <p style='font-size:0.8rem;color:#9CA3AF;margin-bottom:1rem;'>PDF or DOCX &middot; Free &middot; No sign-up required</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Inline uploader
        uploaded_landing = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="landing_uploader", label_visibility="collapsed")
        if uploaded_landing is not None:
            try:
                with st.spinner("Reading your resume..."):
                    fb = uploaded_landing.getvalue()
                    is_pdf = uploaded_landing.name.lower().endswith(".pdf")
                    text = extract_text_from_pdf(fb) if is_pdf else extract_text_from_docx(fb)
                    skills = extract_skills(text)
                st.session_state["resume_text"] = text
                st.session_state["resume_skills"] = skills
                st.session_state["resume_file_type"] = "pdf" if is_pdf else "docx"
                st.session_state["resume_pdf_bytes"] = fb if is_pdf else None
                st.success(f"Resume parsed! Found {len(skills)} skills.")
                goto("job_description")
            except RuntimeError as exc:
                st.error(str(exc))
        
        st.markdown("<p style='font-size:0.75rem;color:#9CA3AF;text-align:center;'>&#128274; Your data is private and never stored permanently.</p>", unsafe_allow_html=True)
    
    with hero_col2:
        # Dashboard preview
        st.markdown("""
        <div class='cp-card' style='padding:1.5rem;animation:slideInRight 0.6s ease forwards;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;'>
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:#10B981;">92</div>
                    <div class="cp-metric-label">ATS Score</div>
                </div>
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:#2563EB;">85</div>
                    <div class="cp-metric-label">Skill Match</div>
                </div>
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:#F59E0B;">78</div>
                    <div class="cp-metric-label">Semantic</div>
                </div>
            </div>
            <div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#6B7280;margin-bottom:0.3rem;">
                    <span>Keyword Match</span><span style="font-weight:600;color:#111827;">88%</span>
                </div>
                <div class="stProgress"><div style="background:#E5E7EB;border-radius:999px;height:8px;overflow:hidden;"><div style="width:88%;background:#2563EB;border-radius:999px;height:8px;"></div></div></div>
            </div>
            <div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#6B7280;margin-bottom:0.3rem;">
                    <span>Experience Relevance</span><span style="font-weight:600;color:#111827;">82%</span>
                </div>
                <div class="stProgress"><div style="background:#E5E7EB;border-radius:999px;height:8px;overflow:hidden;"><div style="width:82%;background:#10B981;border-radius:999px;height:8px;"></div></div></div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#6B7280;margin-bottom:0.3rem;">
                    <span>Education Alignment</span><span style="font-weight:600;color:#111827;">70%</span>
                </div>
                <div class="stProgress"><div style="background:#E5E7EB;border-radius:999px;height:8px;overflow:hidden;"><div style="width:70%;background:#F59E0B;border-radius:999px;height:8px;"></div></div></div>
            </div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
                <span class="cp-badge cp-badge-good">Python</span>
                <span class="cp-badge cp-badge-info">TensorFlow</span>
                <span class="cp-badge cp-badge-purple">Docker</span>
                <span class="cp-badge cp-badge-bad">Kubernetes</span>
                <span class="cp-badge cp-badge-warn">SQL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards row
        features_html = """
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;margin-top:1rem;animation:fadeInUp 0.7s ease forwards;">
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;margin-bottom:0.3rem;">&#9889;</div>
                <div style="font-size:0.8rem;font-weight:600;color:#111827;">Instant Analysis</div>
            </div>
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;margin-bottom:0.3rem;">&#129302;</div>
                <div style="font-size:0.8rem;font-weight:600;color:#111827;">AI Suggestions</div>
            </div>
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;margin-bottom:0.3rem;">&#127919;</div>
                <div style="font-size:0.8rem;font-weight:600;color:#111827;">Smart Matching</div>
            </div>
        </div>
        """
        st.markdown(features_html, unsafe_allow_html=True)


# ============================================================================
# Page 2 — Resume Upload
# ============================================================================
def page_upload_resume():
    render_step_track("upload_resume")
    st.markdown("<h2 style='margin-bottom:0.5rem;'>Upload Your Resume</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;margin-bottom:1.5rem;'>Start by uploading your resume in PDF or DOCX format.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='cp-card' style='padding:2rem;'>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="resume_uploader_2")
    
    if uploaded is not None:
        try:
            with st.spinner("Reading your resume..."):
                file_bytes = uploaded.getvalue()
                is_pdf = uploaded.name.lower().endswith(".pdf")
                text = extract_text_from_pdf(file_bytes) if is_pdf else extract_text_from_docx(file_bytes)
                skills = extract_skills(text)
            st.session_state["resume_text"] = text
            st.session_state["resume_skills"] = skills
            st.session_state["resume_file_type"] = "pdf" if is_pdf else "docx"
            st.session_state["resume_pdf_bytes"] = file_bytes if is_pdf else None
            st.success(f"Resume parsed — found {len(skills)} recognizable skills.")
            if not is_pdf:
                st.caption("Note: layout-preserving optimization (exact design edit) is only available for PDF uploads.")
            if skills:
                st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in skills), unsafe_allow_html=True)
        except RuntimeError as exc:
            st.error(str(exc))
    elif st.session_state["resume_text"]:
        st.info("A resume is already loaded. Upload a new file to replace it.")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_upload"):
            goto("landing")
    with col2:
        can_continue = st.session_state["resume_text"] is not None
        if st.button("Continue", use_container_width=True, type="primary", disabled=not can_continue, key="btn_continue_upload"):
            goto("job_description")


# ============================================================================
# Page 3 — Job Description Input
# ============================================================================
def page_job_description():
    render_step_track("job_description")
    st.markdown("<h2 style='margin-bottom:0.5rem;'>Job Description Source</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;margin-bottom:1.5rem;'>Provide the job description in one of three ways.</p>", unsafe_allow_html=True)

    tab_paste, tab_upload, tab_url = st.tabs(["Paste Job Description", "Upload File", "Job URL"])
    
    with tab_paste:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        jd_text = st.text_area(
            "Paste the job description here", value=st.session_state["jd_text"], height=250,
            placeholder="Copy and paste the full job description...", key="jd_textarea_paste",
        )
        st.session_state["jd_text"] = jd_text
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab_upload:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        jd_file = st.file_uploader("Upload a PDF or DOCX job description", type=["pdf", "docx"], key="jd_file_uploader_2")
        if jd_file is not None:
            try:
                with st.spinner("Reading job description..."):
                    fb = jd_file.getvalue()
                    jd_extracted = extract_text_from_pdf(fb) if jd_file.name.lower().endswith(".pdf") else extract_text_from_docx(fb)
                st.session_state["jd_text"] = jd_extracted
                st.success("File read successfully.")
            except RuntimeError as exc:
                st.error(str(exc))
        if st.session_state["jd_text"]:
            st.session_state["jd_text"] = st.text_area(
                "Extracted text (editable)", value=st.session_state["jd_text"], height=200, key="jd_file_result_2",
            )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab_url:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem;color:#6B7280;margin-bottom:0.75rem;'>Supported: LinkedIn, Indeed, Naukri, Company Careers pages</p>", unsafe_allow_html=True)
        url = st.text_input("Job posting URL", key="jd_url_input_2", placeholder="https://www.linkedin.com/jobs/view/...")
        
        if st.button("Fetch Job Description", key="btn_fetch_jd_url_2"):
            if not url.strip():
                st.warning("Please enter a job URL.")
            elif not re.match(r"^https?://", url.strip(), re.IGNORECASE):
                st.warning("Please enter a valid job URL starting with https://")
            else:
                try:
                    with st.spinner("Fetching job description..."):
                        fetched = extract_jd_from_url(url)
                    st.session_state["jd_text"] = fetched
                    st.success("Fetched successfully.")
                except RuntimeError as exc:
                    st.markdown(f"<div class='cp-status-warn'>{exc}<br><br>Automatic extraction isn't supported for every site (many require login). Try pasting the text manually instead.</div>", unsafe_allow_html=True)
        
        if st.session_state["jd_text"]:
            st.session_state["jd_text"] = st.text_area(
                "Extracted text (editable)", value=st.session_state["jd_text"], height=200, key="jd_url_result_2",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    jd_text = st.session_state["jd_text"]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_jd"):
            goto("upload_resume")
    with col2:
        if st.button("Analyze Resume", use_container_width=True, type="primary", disabled=not jd_text.strip(), key="btn_analyze_jd"):
            try:
                with st.spinner("Comparing your resume against the job description..."):
                    result = compute_match(st.session_state["resume_text"], jd_text)
                st.session_state["match_result"] = result
                goto("results")
            except Exception as exc:
                st.error(f"Something went wrong while analyzing: {exc}")


# ============================================================================
# Page 4 — Results Dashboard
# ============================================================================
def page_results():
    render_step_track("results")
    st.markdown("<h2 style='margin-bottom:1rem;'>Results Dashboard</h2>", unsafe_allow_html=True)
    result = st.session_state["match_result"]
    if result is None:
        st.warning("No analysis yet — go back and provide a job description first.")
        if st.button("Back", key="btn_back_no_result"):
            goto("job_description")
        return

    score = result["match_score"]
    is_eligible = score >= ELIGIBILITY_THRESHOLD

    # Score + eligibility row
    score_col1, score_col2 = st.columns([1, 1.5])
    with score_col1:
        st.markdown("<div class='cp-card' style='display:flex;justify-content:center;padding:2rem;'>", unsafe_allow_html=True)
        st.markdown(circular_score(score, "Resume Match Score"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with score_col2:
        if is_eligible:
            st.markdown("<div class='cp-status-good'>Eligible for Interview! Your resume meets the 75%+ match threshold for this role.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='cp-status-bad'>Not yet eligible for interview (below 75%). Optimize your resume or explore better-fitting roles below.</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        metric_row = st.columns(3)
        with metric_row[0]:
            st.metric("Match Score", f"{score}%")
        with metric_row[1]:
            st.metric("Skills Matched", len(result["matched_skills"]))
        with metric_row[2]:
            st.metric("Skills Missing", len(result["missing_skills"]))
        st.markdown("</div>", unsafe_allow_html=True)

    # Skills breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1rem;margin-bottom:0.75rem;'>Matching Skills</h3>", unsafe_allow_html=True)
        st.progress(min(1.0, result["matched_pct"] / 100))
        if result["matched_skills"]:
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in result["matched_skills"]), unsafe_allow_html=True)
        else:
            st.caption("No overlapping skills detected.")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1rem;margin-bottom:0.75rem;'>Missing Skills</h3>", unsafe_allow_html=True)
        st.progress(min(1.0, result["missing_pct"] / 100))
        if result["missing_skills"]:
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in result["missing_skills"]), unsafe_allow_html=True)
        else:
            st.caption("No missing skills detected!")
        st.markdown("</div>", unsafe_allow_html=True)

    # AI Resume Debate
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;margin-bottom:0.75rem;'>AI Resume Debate</h3>", unsafe_allow_html=True)
    if st.session_state["resume_debate"] is None:
        if st.button("Generate Resume Debate", key="btn_gen_debate"):
            try:
                with st.spinner("Weighing both sides..."):
                    st.session_state["resume_debate"] = generate_resume_debate(st.session_state["resume_text"], st.session_state["jd_text"])
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
    else:
        debate = st.session_state["resume_debate"]
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown("**Why This Resume May Be Shortlisted**")
            for r in debate.get("shortlist_reasons", []):
                st.markdown(f"- {r}")
        with dcol2:
            st.markdown("**Why This Resume May Be Rejected**")
            for r in debate.get("rejection_reasons", []):
                st.markdown(f"- {r}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Next steps
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;margin-bottom:1rem;'>What would you like to do next?</h3>", unsafe_allow_html=True)

    opt1, opt2 = st.columns(2)
    with opt1:
        st.markdown("<div class='cp-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("### Optimize Resume")
        st.markdown("<p style='color:#6B7280;font-size:0.9rem;'>Get AI-powered rewrites tailored to this job description</p>", unsafe_allow_html=True)
        if st.button("Optimize My Resume", use_container_width=True, type="primary", key="btn_option1"):
            goto("resume_optimize")
        st.markdown("</div>", unsafe_allow_html=True)
    with opt2:
        st.markdown("<div class='cp-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("### Find Better Jobs")
        st.markdown("<p style='color:#6B7280;font-size:0.9rem;'>Discover roles that better match your current skills</p>", unsafe_allow_html=True)
        if st.button("Find Matching Jobs", use_container_width=True, key="btn_option2"):
            goto("jobs")
        st.markdown("</div>", unsafe_allow_html=True)

    if is_eligible:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        if st.button("Start AI Assessment", key="btn_direct_assessment"):
            goto("interview")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Back", key="btn_back_results"):
        goto("job_description")


# ============================================================================
# Page 4b — AI Resume Optimizer + Before vs After Comparison
# ============================================================================
def page_resume_optimize():
    render_step_track("resume_optimize")
    st.markdown("<h2 style='margin-bottom:0.5rem;'>Optimize & Compare</h2>", unsafe_allow_html=True)
    
    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_optimize"):
            goto("results")
        return

    is_pdf_origin = st.session_state.get("resume_file_type") == "pdf" and st.session_state["resume_pdf_bytes"]

    # Step 1: Generate optimization
    if st.session_state["optimized_pdf_bytes"] is None:
        st.markdown("<div class='cp-card' style='text-align:center;padding:2rem;'>", unsafe_allow_html=True)
        st.markdown("### Ready to optimize?")
        st.markdown("<p style='color:#6B7280;margin-bottom:1rem;'>The AI will rewrite your resume content while preserving the exact original layout and design.</p>", unsafe_allow_html=True)
        
        if st.button("Generate Optimized Resume", type="primary", key="btn_gen_optimized"):
            try:
                if is_pdf_origin:
                    with st.spinner("Analyzing layout and rewriting content..."):
                        lines = extract_layout_lines(st.session_state["resume_pdf_bytes"])
                        rewrites = generate_layout_constrained_rewrites(lines, st.session_state["jd_text"], result["matched_skills"], result["missing_skills"])
                        if not rewrites:
                            st.warning("No lines could be safely improved. Try a different job description, or your resume is already well-optimized.")
                            st.stop()
                        edited_pdf = apply_layout_preserving_edits(st.session_state["resume_pdf_bytes"], lines, rewrites)
                        optimized_text = lines_to_text(lines, rewrites)
                        original_text = lines_to_text(lines)
                        diff_html = build_resume_diff_html(original_text, optimized_text)
                        section_diffs = build_section_diffs(lines, rewrites)
                    st.session_state["resume_layout_lines"] = lines
                    st.session_state["layout_rewrites"] = rewrites
                    st.session_state["optimized_pdf_bytes"] = edited_pdf
                    st.session_state["optimized_resume_text"] = optimized_text
                    st.session_state["resume_diff_html"] = diff_html
                    st.session_state["section_diffs"] = section_diffs
                    st.success(f"Optimized {len(rewrites)} line(s) while keeping your original design.")
                else:
                    with st.spinner("Rewriting your resume content..."):
                        tailored = generate_tailored_resume(st.session_state["resume_text"], st.session_state["jd_text"], result["matched_skills"], result["missing_skills"])
                        diff_html = build_resume_diff_html(st.session_state["resume_text"], tailored)
                        pdf_bytes = build_resume_pdf(tailored)
                    st.session_state["optimized_resume_text"] = tailored
                    st.session_state["resume_diff_html"] = diff_html
                    st.session_state["optimized_pdf_bytes"] = pdf_bytes
                    st.success("Resume content optimized.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        
        if st.button("Back", key="btn_back_optimize_pre"):
            goto("results")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Step 2: Show Before vs After comparison (MUST appear before download)
    st.markdown("<h3 style='margin-bottom:1rem;'>Before vs After Comparison</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;margin-bottom:1rem;'>Review the changes the AI made to your resume, section by section.</p>", unsafe_allow_html=True)
    
    # Two-panel diff view
    section_diffs = st.session_state.get("section_diffs")
    if section_diffs:
        for sec in section_diffs:
            st.markdown(f"<h4 style='font-size:1rem;margin-bottom:0.5rem;margin-top:1rem;'>{sec['name']}</h4>", unsafe_allow_html=True)
            if sec["changed"] and sec["diff_html"]:
                st.markdown(f"""
                <div class="cp-compare-grid">
                    <div class="cp-compare-original">
                        <div class="cp-compare-label">Original &#10060;</div>
                        <div style="font-size:0.85rem;line-height:1.5;">{sec['diff_html']}</div>
                    </div>
                    <div class="cp-compare-optimized">
                        <div class="cp-compare-label">Optimized &#9989;</div>
                        <div style="font-size:0.85rem;line-height:1.5;">{sec['diff_html']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#9CA3AF;font-size:0.85rem;'>No changes in this section.</p>", unsafe_allow_html=True)
    else:
        # Fallback: show the full diff
        st.markdown("<div class='cp-compare-grid'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="cp-compare-original">
            <div class="cp-compare-label">Original Content (Red = Removed)</div>
            <div style="font-size:0.85rem;line-height:1.5;">{st.session_state['resume_diff_html']}</div>
        </div>
        <div class="cp-compare-optimized">
            <div class="cp-compare-label">Optimized Content (Green = Added)</div>
            <div style="font-size:0.85rem;line-height:1.5;">{st.session_state['resume_diff_html']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Step 3: PDF Preview
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:1rem;'>PDF Preview</h3>", unsafe_allow_html=True)
    b64_pdf = base64.b64encode(st.session_state["optimized_pdf_bytes"]).decode()
    st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" style="border-radius:12px;border:1px solid #E5E7EB;"></iframe>', unsafe_allow_html=True)

    # Step 4: Download options (AFTER comparison)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:0.75rem;'>Download Optimized Resume</h3>", unsafe_allow_html=True)
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button("Download as PDF (design preserved)", data=st.session_state["optimized_pdf_bytes"],
            file_name="optimized_resume.pdf", mime="application/pdf", key="btn_download_pdf",)
    with dcol2:
        st.download_button("Download as DOCX (text only)", data=build_resume_docx(st.session_state["optimized_resume_text"]),
            file_name="optimized_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_download_docx",)
    st.caption("The PDF preserves your exact original design. The DOCX is a clean text re-export.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Step 5: Recalculate score - IMPROVED with score comparison
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:0.75rem;'>Recalculate Match Score</h3>", unsafe_allow_html=True)
    if st.button("Recalculate Score", key="btn_recalculate"):
        try:
            with st.spinner("Recalculating..."):
                recalculated = compute_match(st.session_state["optimized_resume_text"], st.session_state["jd_text"])
            st.session_state["recalculated_match"] = recalculated
            st.session_state["previous_resume_skills"] = st.session_state["resume_skills"][:]
            st.rerun()
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")

    if st.session_state["recalculated_match"]:
        recalc = st.session_state["recalculated_match"]
        orig_score = st.session_state["match_result"]["match_score"] if st.session_state["match_result"] else 0

        # Premium score comparison dashboard
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown("<div class='cp-metric'><div class='cp-metric-label'>Previous Score</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cp-metric-value' style='color:#EF4444;'>{orig_score}%</div></div>", unsafe_allow_html=True)
        with sc2:
            st.markdown("<div class='cp-metric'><div class='cp-metric-label'>Optimized Score</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cp-metric-value' style='color:#10B981;'>{recalc['match_score']}%</div></div>", unsafe_allow_html=True)
        with sc3:
            improvement = round(recalc['match_score'] - orig_score, 1)
            sign = "+" if improvement >= 0 else ""
            color = "#10B981" if improvement >= 0 else "#EF4444"
            st.markdown("<div class='cp-metric'><div class='cp-metric-label'>Improvement</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='cp-metric-value' style='color:{color};'>{sign}{improvement}%</div></div>", unsafe_allow_html=True)

        # Matched & Missing skills badges
        st.markdown("<div style='margin:0.75rem 0;'>", unsafe_allow_html=True)
        if recalc["matched_skills"]:
            st.markdown("**✅ Matched Skills:** " + " ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in recalc["matched_skills"]), unsafe_allow_html=True)
        if recalc["missing_skills"]:
            st.markdown("<br>**❌ Still Missing:** " + " ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in recalc["missing_skills"]), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if recalc["match_score"] >= ELIGIBILITY_THRESHOLD:
            st.markdown("<div class='cp-status-good'>🎉 Your optimized resume now meets the assessment threshold!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='cp-status-warn'>Your resume has improved! Additional preparation is recommended before the assessment.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_optimize"):
            goto("results")
    with col2:
        if st.session_state["recalculated_match"]:
            if st.button("Continue to Career Readiness", use_container_width=True, type="primary", key="btn_optimize_to_readiness"):
                st.session_state["career_readiness_shown"] = False
                goto("career_readiness")
        else:
            st.button("Continue", use_container_width=True, type="primary", disabled=True, key="btn_optimize_disabled")


# ============================================================================
# Page 4c — AI Career Readiness Decision Engine
# ============================================================================
def page_career_readiness():
    st.markdown("<h2 style='margin-bottom:1rem;'>AI Career Readiness Decision</h2>", unsafe_allow_html=True)

    recalc = st.session_state["recalculated_match"]
    if recalc is None:
        st.warning("Please run the Resume Optimization and Recalculate Score first.")
        if st.button("Go to Optimize", key="btn_cr_back_optimize"):
            goto("resume_optimize")
        return

    optimized_score = recalc["match_score"]
    missing_skills = recalc["missing_skills"]

    if optimized_score >= ELIGIBILITY_THRESHOLD:
        # CASE 1: Score >= 75 — Premium Success Card
        st.markdown(f"""
        <div class="cp-success-gradient cp-animate-in">
            <div style="font-size:3rem;margin-bottom:0.75rem;">🎉</div>
            <h3 style="margin-bottom:0.5rem;color:#065F46;">Congratulations!</h3>
            <p style="color:#047857;font-size:1rem;max-width:600px;margin:0 auto;">
                Your optimized resume demonstrates strong alignment with the selected job description.<br>
                You are now ready for the assessment.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Two action cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="cp-decision-card cp-animate-in-left">
                <div class="cp-icon-circle" style="background:#EEF4FF;">
                    📋
                </div>
                <h3 style="font-size:1.1rem;margin-bottom:0.5rem;">Take AI Assessment</h3>
                <p style="color:#6B7280;font-size:0.85rem;margin-bottom:1.25rem;">
                    Evaluate your readiness using an AI-generated assessment 
                    personalized to your resume and target role.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Take AI Assessment", type="primary", use_container_width=True, key="btn_cr_assessment"):
                goto("interview")

        with c2:
            st.markdown("""
            <div class="cp-decision-card cp-animate-in-right">
                <div class="cp-icon-circle" style="background:#FEF3C7;">
                    💼
                </div>
                <h3 style="font-size:1.1rem;margin-bottom:0.5rem;">Find Better Matching Jobs</h3>
                <p style="color:#6B7280;font-size:0.85rem;margin-bottom:1.25rem;">
                    Explore additional opportunities that match your optimized resume.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Find Better Jobs", type="secondary", use_container_width=True, key="btn_cr_jobs"):
                if st.session_state["career_readiness_jobs"] is None:
                    try:
                        with st.spinner("Finding better-matched jobs..."):
                            jobs = recommend_skill_based_jobs(
                                st.session_state["optimized_resume_text"] or st.session_state["resume_text"],
                                st.session_state["resume_skills"]
                            )
                        st.session_state["career_readiness_jobs"] = jobs
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))
                else:
                    goto("career_readiness_jobs")

    else:
        # CASE 2: Score < 75 — AI Mentor Card (never display rejection/negative)
        st.markdown(f"""
        <div class="cp-mentor-card cp-animate-in">
            <div style="font-size:3rem;margin-bottom:0.75rem;">🧭</div>
            <h3 style="margin-bottom:0.5rem;color:#1E40AF;">Your resume has improved significantly</h3>
            <p style="color:#3B82F6;font-size:0.95rem;max-width:650px;margin:0 auto;">
                But additional preparation is recommended before applying for this role.<br>
                Based on your resume and the selected job description, we have prepared 
                two personalized paths to help you become interview-ready.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Two action cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="cp-decision-card cp-animate-in-left">
                <div class="cp-icon-circle" style="background:#EDE9FE;">
                    🎯
                </div>
                <h3 style="font-size:1.1rem;margin-bottom:0.5rem;">Improve My Skills</h3>
                <p style="color:#6B7280;font-size:0.85rem;margin-bottom:1.25rem;">
                    Get a personalized 7-day learning plan and AI mini project 
                    tailored to close your skill gaps.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate My Learning Plan", type="primary", use_container_width=True, key="btn_cr_improve"):
                try:
                    with st.spinner("Generating your personalized 7-day learning plan..."):
                        plan = generate_7day_learning_plan(
                            st.session_state["resume_text"],
                            st.session_state["jd_text"],
                            missing_skills
                        )
                    with st.spinner("Creating a custom AI mini project for you..."):
                        project = generate_ai_mini_project(
                            st.session_state["resume_text"],
                            st.session_state["jd_text"],
                            missing_skills
                        )
                    st.session_state["learning_plan_7day"] = plan
                    st.session_state["ai_mini_project"] = project
                    st.session_state["career_readiness_shown"] = True
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))

        with c2:
            st.markdown("""
            <div class="cp-decision-card cp-animate-in-right">
                <div class="cp-icon-circle" style="background:#FEF3C7;">
                    💼
                </div>
                <h3 style="font-size:1.1rem;margin-bottom:0.5rem;">Find Better Matching Jobs</h3>
                <p style="color:#6B7280;font-size:0.85rem;margin-bottom:1.25rem;">
                    Discover roles that better match your current skills rather 
                    than the original target role.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Find Better Jobs", type="secondary", use_container_width=True, key="btn_cr_improve_jobs"):
                if st.session_state["career_readiness_jobs"] is None:
                    try:
                        with st.spinner("Finding roles that fit your current skills..."):
                            jobs = recommend_skill_based_jobs(
                                st.session_state["optimized_resume_text"] or st.session_state["resume_text"],
                                st.session_state["resume_skills"]
                            )
                        st.session_state["career_readiness_jobs"] = jobs
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))
                else:
                    goto("career_readiness_jobs")

    # Show learning plan and mini project if generated
    if st.session_state["learning_plan_7day"]:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:1rem;'>📚 Your 7-Day Personalized Learning Plan</h3>", unsafe_allow_html=True)
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown(st.session_state["learning_plan_7day"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Mini Project
        project = st.session_state["ai_mini_project"]
        if project:
            st.markdown("<h3 style='margin-bottom:1rem;margin-top:1.5rem;'>🚀 AI Mini Project Recommendation</h3>", unsafe_allow_html=True)
            st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='font-size:1.2rem;'>{project.get('title', 'AI Project')}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#6B7280;'>{project.get('objective', '')}</p>", unsafe_allow_html=True)

            meta = st.columns(3)
            with meta[0]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Difficulty</div><div class='cp-metric-value' style='font-size:1rem;'>{project.get('difficulty', 'Intermediate')}</div></div>", unsafe_allow_html=True)
            with meta[1]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Duration</div><div class='cp-metric-value' style='font-size:1rem;'>{project.get('estimated_duration', '1-2 weeks')}</div></div>", unsafe_allow_html=True)
            with meta[2]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Skills Learned</div><div class='cp-metric-value' style='font-size:1rem;'>{len(project.get('skills_learned', []))}</div></div>", unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:0.95rem;margin-top:1rem;'>Features</h4>", unsafe_allow_html=True)
            for feat in project.get("features", []):
                st.markdown(f"- {feat}")

            st.markdown("<h4 style='font-size:0.95rem;margin-top:0.75rem;'>Technologies</h4>", unsafe_allow_html=True)
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-info'>{t}</span>" for t in project.get("technologies", [])), unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:0.95rem;margin-top:0.75rem;'>Skills You Will Develop</h4>", unsafe_allow_html=True)
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-purple'>{s}</span>" for s in project.get("skills_learned", [])), unsafe_allow_html=True)

            st.markdown(f"<p style='color:#6B7280;font-size:0.9rem;margin-top:0.75rem;'><strong>Expected Outcome:</strong> {project.get('expected_outcome', '')}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Career Progress Tracker - integrated into Improve My Skills workflow
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:1rem;'>📈 Career Progress Tracker</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6B7280;margin-bottom:1rem;'>Upload your improved resume after completing the learning plan to see your progress.</p>", unsafe_allow_html=True)

        improved_upload = st.file_uploader("Upload Improved Resume", type=["pdf", "docx"], key="improved_resume_uploader")
        if improved_upload is not None:
            try:
                with st.spinner("Reading your improved resume..."):
                    fb = improved_upload.getvalue()
                    is_pdf = improved_upload.name.lower().endswith(".pdf")
                    improved_text = extract_text_from_pdf(fb) if is_pdf else extract_text_from_docx(fb)
                    improved_skills = extract_skills(improved_text)

                st.session_state["improved_resume_text"] = improved_text

                with st.spinner("Analyzing your improved resume..."):
                    improved_result = compute_match(improved_text, st.session_state["jd_text"])
                st.session_state["improved_resume_score"] = improved_result

                # Generate improvement summary
                with st.spinner("Generating improvement summary..."):
                    summary = generate_improvement_summary(
                        optimized_score,
                        improved_result["match_score"],
                        st.session_state["resume_skills"],
                        improved_skills,
                        improved_result["missing_skills"]
                    )
                st.session_state["improvement_summary"] = summary

                # Track progress history
                attempt_num = len(st.session_state["progress_history"]) + 1
                st.session_state["progress_history"].append({
                    "attempt": attempt_num,
                    "previous_score": optimized_score,
                    "new_score": improved_result["match_score"],
                    "previous_skills": st.session_state["resume_skills"][:],
                    "new_skills": improved_skills,
                    "missing_skills": improved_result["missing_skills"],
                })

                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

        # Show progress comparison if we have improved resume data
        if st.session_state["improved_resume_score"]:
            imp = st.session_state["improved_resume_score"]
            prev_skills = st.session_state["resume_skills"]
            curr_skills = extract_skills(st.session_state["improved_resume_text"]) if st.session_state["improved_resume_text"] else []
            new_skills_added = [s for s in curr_skills if s not in prev_skills]
            skills_improved = [s for s in prev_skills if s in curr_skills]
            remaining_missing = imp["missing_skills"]
            improvement_pct = round(imp["match_score"] - optimized_score, 1)

            # Premium progress dashboard
            st.markdown("<div class='cp-progress-dashboard'>", unsafe_allow_html=True)
            st.markdown("<h4 style='margin-bottom:1rem;'>Progress Dashboard</h4>", unsafe_allow_html=True)

            dash_cols = st.columns(4)
            with dash_cols[0]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Previous Score</div><div class='cp-metric-value' style='color:#EF4444;'>{optimized_score}%</div></div>", unsafe_allow_html=True)
            with dash_cols[1]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Current Score</div><div class='cp-metric-value' style='color:#10B981;'>{imp['match_score']}%</div></div>", unsafe_allow_html=True)
            with dash_cols[2]:
                sign = "+" if improvement_pct >= 0 else ""
                clr = "#10B981" if improvement_pct >= 0 else "#EF4444"
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>Improvement</div><div class='cp-metric-value' style='color:{clr};'>{sign}{improvement_pct}%</div></div>", unsafe_allow_html=True)
            with dash_cols[3]:
                st.markdown(f"<div class='cp-metric'><div class='cp-metric-label'>New Skills</div><div class='cp-metric-value' style='color:#2563EB;'>{len(new_skills_added)}</div></div>", unsafe_allow_html=True)

            # Skills breakdown
            sk_col1, sk_col2, sk_col3 = st.columns(3)
            with sk_col1:
                if new_skills_added:
                    st.markdown("**🆕 New Skills Added:** " + " ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in new_skills_added), unsafe_allow_html=True)
            with sk_col2:
                if skills_improved:
                    st.markdown("**✅ Improved Skills:** " + " ".join(f"<span class='cp-badge cp-badge-info'>{s}</span>" for s in skills_improved), unsafe_allow_html=True)
            with sk_col3:
                if remaining_missing:
                    st.markdown("**❌ Remaining Missing:** " + " ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in remaining_missing), unsafe_allow_html=True)

            # AI Summary
            if st.session_state["improvement_summary"]:
                st.markdown(f"<div style='background:#F8FAFC;border-radius:12px;padding:1rem;margin-top:0.75rem;font-size:0.9rem;color:#374151;'><strong>🤖 AI Summary:</strong> {st.session_state['improvement_summary']}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Progress history chart
            if len(st.session_state["progress_history"]) > 0:
                st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-bottom:0.75rem;'>Progress History</h4>", unsafe_allow_html=True)
                hist = st.session_state["progress_history"]
                chart_data = {
                    "Attempt": [h["attempt"] for h in hist],
                    "Score": [h["new_score"] for h in hist],
                }
                st.line_chart(chart_data, x="Attempt", y="Score", height=200)
                st.markdown("</div>", unsafe_allow_html=True)

            # Check if ready for assessment
            if imp["match_score"] >= ELIGIBILITY_THRESHOLD:
                st.markdown(f"""
                <div class="cp-success-gradient">
                    <div style="font-size:3rem;margin-bottom:0.75rem;">🎉</div>
                    <h3 style="margin-bottom:0.5rem;color:#065F46;">Congratulations!</h3>
                    <p style="color:#047857;font-size:1rem;">You are now interview-ready! Your resume score of {imp['match_score']}% meets the assessment threshold.</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Unlock AI Assessment", type="primary", use_container_width=True, key="btn_unlock_assessment"):
                    goto("interview")
            else:
                st.markdown("<div class='cp-status-warn'>Keep going! You're making great progress. Continue with the learning plan and try uploading another improved resume.</div>", unsafe_allow_html=True)
                # Regenerate learning plan + mini project based on remaining missing skills
                if st.button("Regenerate Learning Plan for Remaining Skills", type="secondary", key="btn_regenerate_plan"):
                    try:
                        with st.spinner("Regenerating personalized learning plan..."):
                            new_plan = generate_7day_learning_plan(
                                st.session_state["improved_resume_text"],
                                st.session_state["jd_text"],
                                remaining_missing
                            )
                        with st.spinner("Creating a new AI mini project..."):
                            new_project = generate_ai_mini_project(
                                st.session_state["improved_resume_text"],
                                st.session_state["jd_text"],
                                remaining_missing
                            )
                        st.session_state["learning_plan_7day"] = new_plan
                        st.session_state["ai_mini_project"] = new_project
                        # Reset for next attempt
                        st.session_state["resume_text"] = st.session_state["improved_resume_text"]
                        st.session_state["resume_skills"] = curr_skills
                        st.session_state["improved_resume_text"] = None
                        st.session_state["improved_resume_score"] = None
                        st.session_state["recalculated_match"] = None
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

    # Show career readiness jobs if generated
    if st.session_state["career_readiness_jobs"] and st.session_state.get("page") == "career_readiness":
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:1rem;'>💼 Recommended Jobs Based on Your Skills</h3>", unsafe_allow_html=True)
        for job in st.session_state["career_readiness_jobs"]:
            st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
            title_company = job.get("job_title", "Role")
            if job.get("company"):
                title_company += f" at {job['company']}"
            st.markdown(f"<h3 style='font-size:1.1rem;'>{title_company}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Estimated Match:** {job.get('estimated_match_pct', '-')}%")
            st.progress(min(1.0, (job.get("estimated_match_pct") or 0) / 100))
            st.caption(job.get("reason", ""))
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in job.get("skills_present", [])), unsafe_allow_html=True)
            st.markdown(" ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in job.get("skills_missing", [])), unsafe_allow_html=True)
            urls = job.get("apply_urls", {})
            for site in ("LinkedIn", "Indeed", "Naukri", "Company Careers"):
                if site in urls:
                    st.link_button(f"Apply on {site}", urls[site], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Navigation buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Optimize", use_container_width=True, key="btn_cr_back"):
            goto("resume_optimize")
    with col2:
        if st.button("Career Toolkit", use_container_width=True, key="btn_cr_toolkit"):
            goto("toolkit")


# ============================================================================
# Page 4d — Career Readiness Jobs (separate view)
# ============================================================================
def page_career_readiness_jobs():
    st.markdown("<h2 style='margin-bottom:1rem;'>💼 Recommended Jobs</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;margin-bottom:1.5rem;'>Roles that better match your current skills and optimized resume.</p>", unsafe_allow_html=True)

    if st.session_state["career_readiness_jobs"] is None:
        try:
            with st.spinner("Finding roles that fit your skills..."):
                jobs = recommend_skill_based_jobs(
                    st.session_state["optimized_resume_text"] or st.session_state["resume_text"],
                    st.session_state["resume_skills"]
                )
            st.session_state["career_readiness_jobs"] = jobs
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))
            if st.button("Back", key="btn_crj_back_fail"):
                goto("career_readiness")
            return

    for job in st.session_state["career_readiness_jobs"]:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        title_company = job.get("job_title", "Role")
        if job.get("company"):
            title_company += f" at {job['company']}"
        st.markdown(f"<h3 style='font-size:1.1rem;'>{title_company}</h3>", unsafe_allow_html=True)
        st.markdown(f"**Estimated Match:** {job.get('estimated_match_pct', '-')}%")
        st.progress(min(1.0, (job.get("estimated_match_pct") or 0) / 100))
        st.caption(job.get("reason", ""))
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in job.get("skills_present", [])), unsafe_allow_html=True)
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in job.get("skills_missing", [])), unsafe_allow_html=True)
        urls = job.get("apply_urls", {})
        for site in ("LinkedIn", "Indeed", "Naukri", "Company Careers"):
            if site in urls:
                st.link_button(f"Apply on {site}", urls[site], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_crj_back"):
            goto("career_readiness")
    with col2:
        if st.button("Career Toolkit", use_container_width=True, key="btn_crj_toolkit"):
            goto("toolkit")


# ============================================================================
# Page 5 — Interview Test
# ============================================================================
def page_interview():
    st.markdown("<h2 style='margin-bottom:1rem;'>Personalized Placement Assessment</h2>", unsafe_allow_html=True)

    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_interview_blocked"):
            goto("results")
        return

    effective_result = st.session_state["recalculated_match"] or result
    if effective_result["match_score"] < ELIGIBILITY_THRESHOLD:
        st.markdown(f"<div class='cp-status-bad'>Your current score ({effective_result['match_score']}%) is below the {ELIGIBILITY_THRESHOLD}% threshold required for the assessment.</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Optimize Resume", type="primary", key="btn_to_optimize"):
                goto("resume_optimize")
        with col2:
            if st.button("Find Better Jobs", key="btn_to_jobs"):
                goto("jobs")
        return

    if st.session_state["interview"] is None:
        with st.expander("Optional: make it company-specific"):
            st.session_state["company_name"] = st.text_input("Company name", value=st.session_state["company_name"], key="company_name_input")
            st.session_state["company_url"] = st.text_input("Company About/Careers page URL (optional)", value=st.session_state["company_url"], key="company_url_input")
            if st.button("Fetch Company Context", key="btn_fetch_company"):
                try:
                    with st.spinner("Reading company page..."):
                        st.session_state["company_context"] = fetch_company_context(st.session_state["company_url"])
                    st.success("Fetched!")
                except RuntimeError as exc:
                    st.warning(str(exc))

        if st.button("Generate My Personalized Interview", type="primary", key="btn_gen_interview"):
            jd_lower = st.session_state["jd_text"].lower()
            requires_coding = any(kw in jd_lower for kw in ["software", "developer", "engineer", "coding", "programming", "sde"])
            try:
                with st.spinner("Generating assessment..."):
                    interview = generate_interview(st.session_state["resume_text"], st.session_state["jd_text"], requires_coding, company_context=st.session_state["company_context"])
                st.session_state["interview"] = interview
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        if st.button("Back", key="btn_back_interview_pre"):
            goto("results")
        return

    interview = st.session_state["interview"]
    answers = st.session_state["interview_answers"]

    # MCQ sections in cards
    for section_key, section_title, icon in [("aptitude", "Aptitude", "🧮"), ("verbal", "Verbal Ability", "🗣️"), ("reasoning", "Logical Reasoning", "🧩")]:
        st.markdown(f"<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-size:1rem;margin-bottom:0.75rem;'>{icon} {section_title}</h3>", unsafe_allow_html=True)
        for i, q in enumerate(interview.get(section_key, [])):
            answers[f"{section_key}_{i}"] = st.radio(f"Q{i + 1}. {q['question']}", q["options"], key=f"{section_key}_radio_{i}", index=None)
        st.markdown("</div>", unsafe_allow_html=True)

    # Technical
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;margin-bottom:0.75rem;'>Technical Questions</h3>", unsafe_allow_html=True)
    for i, q in enumerate(interview.get("technical", [])):
        answers[f"tech_{i}"] = st.text_area(f"Q{i + 1}. {q}", key=f"tech_answer_{i}")
    if interview.get("coding_question"):
        st.markdown("<h3 style='font-size:1rem;margin-bottom:0.75rem;margin-top:1rem;'>Coding Question</h3>", unsafe_allow_html=True)
        st.code(interview["coding_question"], language=None)
        answers["coding"] = st.text_area("Your solution", key="coding_answer", height=180)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state["interview_answers"] = answers

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_interview"):
            goto("results")
    with col2:
        if st.button("Submit for Evaluation", use_container_width=True, type="primary", key="btn_submit_interview"):
            try:
                with st.spinner("Evaluating your responses..."):
                    evaluation = evaluate_answers(st.session_state["resume_text"], st.session_state["jd_text"], interview, answers)
                st.session_state["evaluation"] = evaluation
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    evaluation = st.session_state["evaluation"]
    if evaluation:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='cp-card' style='display:flex;justify-content:center;'>", unsafe_allow_html=True)
        st.markdown(circular_score(evaluation.get("overall_score", 0), "Overall Score"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='cp-status-{'good' if evaluation.get('readiness_level') in ('Ready','Highly Ready') else 'warn'}'>Readiness Level: {evaluation.get('readiness_level', '-')}</div>", unsafe_allow_html=True)

        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        cat = evaluation.get("category_scores", {})
        cats = st.columns(5)
        for col, (key, label) in zip(cats, [("aptitude", "🧮 Aptitude"), ("verbal", "🗣️ Verbal"), ("reasoning", "🧩 Reasoning"), ("technical", "🛠️ Technical"), ("coding", "💻 Coding")]):
            with col:
                val = cat.get(key)
                st.metric(label, f"{val}%" if val is not None else "N/A")
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='cp-card'><strong>Strong Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("strong_areas", [])) + "</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='cp-card'><strong>Weak Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("weak_areas", [])) + "</div>", unsafe_allow_html=True)

        if st.button("Continue to Mini Mock Interview", type="primary", key="btn_interview_to_mock"):
            goto("mock_interview")


# ============================================================================
# Page 5b — Mini Mock Interview
# ============================================================================
def page_mock_interview():
    st.markdown("<h2 style='margin-bottom:0.5rem;'>Mini Mock Interview</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;margin-bottom:1.5rem;'>Answer each question as if in a real spoken interview.</p>", unsafe_allow_html=True)

    if st.session_state["match_result"] is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_mock"):
            goto("results")
        return

    if st.session_state["mock_interview_questions"] is None:
        if st.button("Start Mini Mock Interview", type="primary", key="btn_gen_mock"):
            try:
                with st.spinner("Preparing questions..."):
                    questions = generate_mock_interview_questions(st.session_state["resume_text"], st.session_state["jd_text"])
                st.session_state["mock_interview_questions"] = questions
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        if st.button("Back", key="btn_back_mock_pre"):
            goto("interview")
        return

    questions = st.session_state["mock_interview_questions"]
    answers = st.session_state["mock_interview_answers"]

    for i, q in enumerate(questions):
        st.markdown(f"<div class='cp-card'><strong>Q{i + 1}.</strong> {q}</div>", unsafe_allow_html=True)
        answers[str(i)] = st.text_area(f"Your answer", key=f"mock_answer_{i}", height=100, label_visibility="collapsed")
    st.session_state["mock_interview_answers"] = answers

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_mock"):
            goto("interview")
    with col2:
        if st.button("Submit for Evaluation", use_container_width=True, type="primary", key="btn_submit_mock"):
            try:
                with st.spinner("Evaluating..."):
                    ordered_answers = [answers.get(str(i), "") for i in range(len(questions))]
                    evaluation = evaluate_mock_interview(st.session_state["resume_text"], st.session_state["jd_text"], questions, ordered_answers)
                st.session_state["mock_interview_evaluation"] = evaluation
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    evaluation = st.session_state["mock_interview_evaluation"]
    if evaluation:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='cp-card' style='display:flex;justify-content:center;'>", unsafe_allow_html=True)
        st.markdown(circular_score(evaluation.get("overall_readiness_score", 0), "Interview Readiness"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        scores = st.columns(3)
        with scores[0]:
            st.metric("Communication", f"{evaluation.get('communication_score', '-')}%")
        with scores[1]:
            st.metric("Technical", f"{evaluation.get('technical_understanding_score', '-')}%")
        with scores[2]:
            st.metric("Confidence", f"{evaluation.get('confidence_score', '-')}%")

        st.markdown("<div class='cp-card'><strong>Feedback</strong>" + "".join(f"<br>- {f}" for f in evaluation.get("feedback", [])) + "</div>", unsafe_allow_html=True)

        if st.button("Career Toolkit", key="btn_mock_to_toolkit"):
            goto("toolkit")


# ============================================================================
# Page 6 — Recommended Jobs
# ============================================================================
def page_jobs():
    st.markdown("<h2 style='margin-bottom:1rem;'>Recommended Jobs</h2>", unsafe_allow_html=True)
    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run an analysis first.")
        if st.button("Back", key="btn_back_no_jobs"):
            goto("results")
        return

    if st.session_state["recommended_jobs"] is None:
        if st.button("Find Better-Matched Jobs", type="primary", key="btn_find_jobs"):
            try:
                with st.spinner("Finding roles that fit your skills..."):
                    jobs = recommend_jobs(st.session_state["resume_text"], st.session_state["resume_skills"], result["match_score"])
                st.session_state["recommended_jobs"] = jobs
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        if st.button("Back", key="btn_back_jobs_pre"):
            goto("results")
        return

    for job in st.session_state["recommended_jobs"]:
        st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-size:1.1rem;'>{job.get('job_title', 'Role')}</h3>", unsafe_allow_html=True)
        st.markdown(f"**Estimated Match:** {job.get('estimated_match_pct', '-')}%")
        st.progress(min(1.0, (job.get("estimated_match_pct") or 0) / 100))
        st.caption(job.get("reason", ""))
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in job.get("skills_present", [])), unsafe_allow_html=True)
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in job.get("skills_missing", [])), unsafe_allow_html=True)
        links = job.get("apply_links", {})
        for site in ("LinkedIn", "Indeed", "Naukri"):
            if site in links:
                st.link_button(f"Apply on {site}", links[site], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key="btn_back_jobs_done"):
            goto("results")
    with col2:
        if st.button("Career Toolkit", key="btn_jobs_to_toolkit"):
            goto("toolkit")


# ============================================================================
# Page 7 — Career Toolkit
# ============================================================================
def page_toolkit():
    st.markdown("<h2 style='margin-bottom:1rem;'>Career Toolkit</h2>", unsafe_allow_html=True)

    if st.session_state["match_result"] is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_toolkit"):
            goto("results")
        return

    # Outreach Email
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;'>Professional Outreach Email</h3>", unsafe_allow_html=True)
    if st.button("Generate Email", key="btn_gen_email"):
        try:
            with st.spinner("Drafting..."):
                st.session_state["outreach_email"] = generate_outreach_email(st.session_state["resume_text"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["outreach_email"]:
        st.text_area("Draft", st.session_state["outreach_email"], height=180, key="email_display")
    st.markdown("</div>", unsafe_allow_html=True)

    # Learning Roadmap
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;'>Learning Roadmap</h3>", unsafe_allow_html=True)
    if st.button("Generate Roadmap", key="btn_gen_roadmap"):
        try:
            with st.spinner("Building roadmap..."):
                st.session_state["learning_roadmap"] = generate_learning_roadmap(st.session_state["match_result"]["missing_skills"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["learning_roadmap"]:
        st.markdown(st.session_state["learning_roadmap"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Bullet Rewrites
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;'>Bullet Rewrite Suggestions</h3>", unsafe_allow_html=True)
    if st.button("Generate Rewrites", key="btn_gen_rewrites"):
        try:
            with st.spinner("Analyzing..."):
                st.session_state["bullet_rewrites"] = generate_bullet_rewrites(st.session_state["resume_text"], st.session_state["match_result"]["missing_skills"], st.session_state["jd_text"])
            if not st.session_state["bullet_rewrites"]:
                st.info("Your resume already aligns well! No rewrites needed.")
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["bullet_rewrites"]:
        for r in st.session_state["bullet_rewrites"]:
            st.markdown(f"**Original:** {r.get('original', '')}")
            st.markdown(f"**Rewritten:** {r.get('rewritten', '')}")
            st.caption(r.get("why", ""))
            st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

    # Download Report
    st.markdown("<div class='cp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1rem;'>Download Report</h3>", unsafe_allow_html=True)
    report_md = build_report_markdown(st.session_state)
    st.download_button("Download Career Report (.md)", data=report_md, file_name="careerpilot_report.md", mime="text/markdown", key="btn_download_report")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Back", key="btn_back_toolkit"):
        goto("results")


# ============================================================================
# Sidebar Navigation + Router
# ============================================================================
if st.session_state["page"] != "landing":
    with st.sidebar:
        st.markdown("### CareerPilot AI")
        st.caption("Analyze &bull; Prepare &bull; Apply")
        nav_pages = [
            ("upload_resume", "Upload Resume"),
            ("job_description", "Job Description"),
            ("results", "Results"),
            ("resume_optimize", "Optimize"),
            ("career_readiness", "Career Readiness"),
            ("interview", "Assessment"),
            ("jobs", "Jobs"),
            ("toolkit", "Toolkit"),
        ]
        for page_key, page_label in nav_pages:
            active = "background: #EEF4FF; color: #2563EB; font-weight: 600;" if st.session_state["page"] == page_key else ""
            if st.button(page_label, key=f"nav_{page_key}"):
                goto(page_key)
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Start Over", key="btn_reset"):
            reset_all()

PAGES = {
    "landing": page_landing,
    "upload_resume": page_upload_resume,
    "job_description": page_job_description,
    "results": page_results,
    "resume_optimize": page_resume_optimize,
    "career_readiness": page_career_readiness,
    "career_readiness_jobs": page_career_readiness_jobs,
    "interview": page_interview,
    "mock_interview": page_mock_interview,
    "jobs": page_jobs,
    "toolkit": page_toolkit,
}

PAGES[st.session_state["page"]]()

