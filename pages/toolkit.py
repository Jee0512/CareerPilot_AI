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
from modules.ui_components import (
    inject_tailwind, render_top_navbar, render_step_track, circular_score,
    STEP_SEQUENCE, STEP_LABELS,
    section_heading, section_title,
    status_banner, privacy_note,
    badge_list, labeled_badges,
    metric_value, score_comparison,
    render_job_card, compare_grid,
    decision_card, success_gradient, mentor_card,
    divider,
)


section_heading("Career Toolkit")
if st.session_state["match_result"] is None:
    st.warning("Run a resume analysis first.")
    if st.button("Back", key="btn_back_no_toolkit"):
        st.switch_page("pages/results.py")
st.stop()
# Outreach Email
with st.container(border=True):
    section_title("Professional Outreach Email")
    if st.button("Generate Email", key="btn_gen_email"):
        try:
            with st.spinner("Drafting..."):
                st.session_state["outreach_email"] = generate_outreach_email(st.session_state["resume_text"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["outreach_email"]:
        st.text_area("Draft", st.session_state["outreach_email"], height=180, key="email_display")
# Learning Roadmap
with st.container(border=True):
    section_title("Learning Roadmap")
    if st.button("Generate Roadmap", key="btn_gen_roadmap"):
        try:
            with st.spinner("Building roadmap..."):
                st.session_state["learning_roadmap"] = generate_learning_roadmap(st.session_state["match_result"]["missing_skills"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["learning_roadmap"]:
        st.markdown(st.session_state["learning_roadmap"])
# Bullet Rewrites
with st.container(border=True):
    section_title("Bullet Rewrite Suggestions")
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
# Download Report
with st.container(border=True):
    section_title("Download Report")
    report_md = build_report_markdown(st.session_state)
    st.download_button("Download Career Report (.md)", data=report_md, file_name="careerpilot_report.md", mime="text/markdown", key="btn_download_report")
if st.button("Back", key="btn_back_toolkit"):
    st.switch_page("pages/results.py")
# Sidebar Navigation + Router


