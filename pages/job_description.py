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
    render_step_track, render_page_header
)

render_step_track("job_description")
render_page_header("Job Description Source", "Provide the job description in one of three ways.")
tab_paste, tab_upload, tab_url = st.tabs(["Paste Job Description", "Upload File", "Job URL"])
with tab_paste:
    with st.container(border=True):
        jd_text = st.text_area(
            "Paste the job description here", value=st.session_state["jd_text"], height=250,
            placeholder="Copy and paste the full job description...", key="jd_textarea_paste",
        )
        st.session_state["jd_text"] = jd_text
with tab_upload:
    with st.container(border=True):
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
with tab_url:
    with st.container(border=True):
        st.markdown('<p style="font-size:0.85rem;color:var(--cp-color-text-muted);margin-bottom:0.5rem;">Supported: LinkedIn, Indeed, Naukri, Company Careers pages</p>', unsafe_allow_html=True)
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
                    st.warning(f"{exc}\n\nAutomatic extraction isn't supported for every site (many require login). Try pasting the text manually instead.")

        if st.session_state["jd_text"]:
            st.session_state["jd_text"] = st.text_area(
                "Extracted text (editable)", value=st.session_state["jd_text"], height=200, key="jd_url_result_2",
            )
jd_text = st.session_state["jd_text"]
col1, col2 = st.columns(2)
with col1:
    if st.button("Back", use_container_width=True, key="btn_back_jd"):
        st.switch_page("pages/upload_resume.py")
with col2:
    if st.button("Analyze Resume", use_container_width=True, type="primary", disabled=not jd_text.strip(), key="btn_analyze_jd"):
        try:
            with st.spinner("Comparing your resume against the job description..."):
                result = compute_match(st.session_state["resume_text"], jd_text)
            st.session_state["match_result"] = result
            st.switch_page("pages/results.py")
        except Exception as exc:
            st.error(f"Something went wrong while analyzing: {exc}")
# Page 4 ΓÇö Results Dashboard


