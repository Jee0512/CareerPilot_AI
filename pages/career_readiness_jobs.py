import re
import streamlit as st
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
from ui.components import (
    render_page_header, render_job_card
)


render_page_header("💼 Recommended Jobs")
st.caption("Roles that better match your current skills and optimized resume.")
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
            st.switch_page("pages/career_readiness.py")
st.stop()
for job in st.session_state["career_readiness_jobs"]:
    render_job_card(job, apply_key="apply_urls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Back", use_container_width=True, key="btn_crj_back"):
        st.switch_page("pages/career_readiness.py")
with col2:
    if st.button("Career Toolkit", use_container_width=True, key="btn_crj_toolkit"):
        st.switch_page("pages/toolkit.py")
# Page 5 ΓÇö Interview Test


