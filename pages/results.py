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


render_step_track("results")
section_heading("Results Dashboard")
result = st.session_state["match_result"]
if result is None:
    st.warning("No analysis yet ΓÇö go back and provide a job description first.")
    if st.button("Back", key="btn_back_no_result"):
        st.switch_page("pages/job_description.py")
st.stop()
score = result["match_score"]
is_eligible = score >= ELIGIBILITY_THRESHOLD
# Score + eligibility row
score_col1, score_col2 = st.columns([1, 1.5])
with score_col1:
    with st.container(border=True):
        st.markdown(circular_score(score, "Resume Match Score"), unsafe_allow_html=True)
with score_col2:
    if is_eligible:
        status_banner("Eligible for Interview! Your resume meets the 75%+ match threshold for this role.", "good")
    else:
        status_banner("Not yet eligible for interview (below 75%). Optimize your resume or explore better-fitting roles below.", "bad")
    with st.container(border=True):
        metric_row = st.columns(3)
        with metric_row[0]:
            st.metric("Match Score", f"{score}%")
        with metric_row[1]:
            st.metric("Skills Matched", len(result["matched_skills"]))
        with metric_row[2]:
            st.metric("Skills Missing", len(result["missing_skills"]))
# Skills breakdown
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        section_title("Matching Skills")
        st.progress(min(1.0, result["matched_pct"] / 100))
        if result["matched_skills"]:
            badge_list(result["matched_skills"], "good")
        else:
            st.caption("No overlapping skills detected.")
with col2:
    with st.container(border=True):
        section_title("Missing Skills")
        st.progress(min(1.0, result["missing_pct"] / 100))
        if result["missing_skills"]:
            badge_list(result["missing_skills"], "bad")
        else:
            st.caption("No missing skills detected!")
# AI Resume Debate
with st.container(border=True):
    section_title("AI Resume Debate")
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
# Next steps
divider()
section_heading("What would you like to do next?")
opt1, opt2 = st.columns(2)
with opt1:
    with st.container(border=True):
        st.markdown("### Optimize Resume")
        st.caption("Get AI-powered rewrites tailored to this job description")
        if st.button("Optimize My Resume", use_container_width=True, type="primary", key="btn_option1"):
            st.switch_page("pages/resume_optimize.py")
with opt2:
    with st.container(border=True):
        st.markdown("### Find Better Jobs")
        st.caption("Discover roles that better match your current skills")
        if st.button("Find Matching Jobs", use_container_width=True, key="btn_option2"):
            st.switch_page("pages/jobs.py")
if is_eligible:
    with st.container(border=True):
        if st.button("Start AI Assessment", key="btn_direct_assessment"):
            st.switch_page("pages/interview.py")
if st.button("Back", key="btn_back_results"):
    st.switch_page("pages/job_description.py")
# Page 4b ΓÇö AI Resume Optimizer + Before vs After Comparison


