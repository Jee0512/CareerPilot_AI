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


section_heading("Mini Mock Interview", "Answer each question as if in a real spoken interview.")
if st.session_state["match_result"] is None:
    st.warning("Run a resume analysis first.")
    if st.button("Back", key="btn_back_no_mock"):
        st.switch_page("pages/results.py")
st.stop()
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
        st.switch_page("pages/interview.py")
st.stop()
questions = st.session_state["mock_interview_questions"]
answers = st.session_state["mock_interview_answers"]
for i, q in enumerate(questions):
    with st.container(border=True):
        st.markdown(f"<strong>Q{i + 1}.</strong> {q}", unsafe_allow_html=True)
    answers[str(i)] = st.text_area(f"Your answer", key=f"mock_answer_{i}", height=100, label_visibility="collapsed")
st.session_state["mock_interview_answers"] = answers
col1, col2 = st.columns(2)
with col1:
    if st.button("Back", use_container_width=True, key="btn_back_mock"):
        st.switch_page("pages/interview.py")
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
    divider()
    with st.container(border=True):
        st.markdown(circular_score(evaluation.get("overall_readiness_score", 0), "Interview Readiness"), unsafe_allow_html=True)
    scores = st.columns(3)
    with scores[0]:
        st.metric("Communication", f"{evaluation.get('communication_score', '-')}%")
    with scores[1]:
        st.metric("Technical", f"{evaluation.get('technical_understanding_score', '-')}%")
    with scores[2]:
        st.metric("Confidence", f"{evaluation.get('confidence_score', '-')}%")
    with st.container(border=True):
        st.markdown("<strong>Feedback</strong>" + "".join(f"<br>- {f}" for f in evaluation.get("feedback", [])), unsafe_allow_html=True)
    if st.button("Career Toolkit", key="btn_mock_to_toolkit"):
        st.switch_page("pages/toolkit.py")
# Page 6 ΓÇö Recommended Jobs


