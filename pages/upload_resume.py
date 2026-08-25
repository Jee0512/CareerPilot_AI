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
    render_step_track, render_page_header, render_badge_list
)

render_step_track("upload_resume")
render_page_header("Upload Your Resume", "Start by uploading your resume in PDF or DOCX format.")
with st.container(border=True):
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
            st.success(f"Resume parsed ΓÇö found {len(skills)} recognizable skills.")
            if not is_pdf:
                st.caption("Note: layout-preserving optimization (exact design edit) is only available for PDF uploads.")
            if skills:
                render_badge_list(skills, "good")
        except RuntimeError as exc:
            st.error(str(exc))
    elif st.session_state["resume_text"]:
        st.info("A resume is already loaded. Upload a new file to replace it.")
col1, col2 = st.columns(2)
with col1:
    if st.button("Reset", use_container_width=True, key="btn_reset_upload"):
        st.session_state["resume_text"] = None
        st.session_state["resume_skills"] = []
        st.rerun()
with col2:
    can_continue = st.session_state["resume_text"] is not None
    if st.button("Continue", use_container_width=True, type="primary", disabled=not can_continue, key="btn_continue_upload"):
        st.switch_page("pages/job_description.py")
# Page 3 ΓÇö Job Description Input


