"""

CareerPilot AI ΓÇö app.py

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

import time



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



st.set_page_config(page_title="CareerPilot AI", page_icon="≡ƒº¡", layout="wide")



# ============================================================================

# Load external CSS, Tailwind CDN & reusable UI components

# ============================================================================

from pathlib import Path

from modules.ui_components import (

    render_top_navbar, render_step_track, circular_score,
    STEP_SEQUENCE, STEP_LABELS,
    section_heading, section_title,
    status_banner, privacy_note,
    badge_list, labeled_badges,
    metric_value, score_comparison,
    render_job_card, compare_grid,
    decision_card, success_gradient, mentor_card,
    divider,

)



def get_custom_css():
    # Load legacy CSS
    legacy_css_path = Path(__file__).parent / "assets" / "style.css"
    legacy_css = legacy_css_path.read_text(encoding="utf-8")
    
    # Load new design foundation CSS
    tokens_path = Path(__file__).parent / "styles" / "tokens.css"
    base_path = Path(__file__).parent / "styles" / "base.css"
    streamlit_path = Path(__file__).parent / "styles" / "streamlit.css"
    
    new_css = "\n".join([
        tokens_path.read_text(encoding="utf-8") if tokens_path.exists() else "",
        base_path.read_text(encoding="utf-8") if base_path.exists() else "",
        streamlit_path.read_text(encoding="utf-8") if streamlit_path.exists() else ""
    ])
    
    return legacy_css + "\n" + new_css

st.markdown(f"<style>{get_custom_css()}</style>", unsafe_allow_html=True)



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




# ============================================================================
# Navigation Setup
# ============================================================================

pages = {
    "CareerPilot": [
        st.Page("pages/landing.py", title="Home", default=True),
        st.Page("pages/upload_resume.py", title="Upload Resume"),
        st.Page("pages/job_description.py", title="Job Description"),
        st.Page("pages/results.py", title="Results"),
        st.Page("pages/resume_optimize.py", title="Optimize"),
        st.Page("pages/career_readiness.py", title="Career Readiness"),
        st.Page("pages/career_readiness_jobs.py", title="Recommended Jobs"),
        st.Page("pages/interview.py", title="Assessment"),
        st.Page("pages/mock_interview.py", title="Mock Interview"),
        st.Page("pages/jobs.py", title="Find Jobs"),
        st.Page("pages/toolkit.py", title="Career Toolkit"),
    ]
}

pg = st.navigation(pages)
pg.run()
