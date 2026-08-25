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


section_heading("Personalized Placement Assessment")
result = st.session_state["match_result"]
if result is None:
    st.warning("Run a resume analysis first.")
    if st.button("Back", key="btn_back_interview_blocked"):
        st.switch_page("pages/results.py")
st.stop()
effective_result = st.session_state["recalculated_match"] or result
if effective_result["match_score"] < ELIGIBILITY_THRESHOLD:
    status_banner(f"Your current score ({effective_result['match_score']}%) is below the {ELIGIBILITY_THRESHOLD}% threshold required for the assessment.", "bad")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Optimize Resume", type="primary", key="btn_to_optimize"):
            st.switch_page("pages/resume_optimize.py")
    with col2:
        if st.button("Find Better Jobs", key="btn_to_jobs"):
            st.switch_page("pages/jobs.py")
st.stop()
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
        st.switch_page("pages/results.py")
st.stop()
interview = st.session_state["interview"]
answers = st.session_state["interview_answers"]
# MCQ sections in cards
for section_key, section_title_text, icon in [("aptitude", "Aptitude", "≡ƒº«"), ("verbal", "Verbal Ability", "≡ƒùú∩╕Å"), ("reasoning", "Logical Reasoning", "≡ƒº⌐")]:
    with st.container(border=True):
        section_title(section_title_text, icon=icon)
        for i, q in enumerate(interview.get(section_key, [])):
            answers[f"{section_key}_{i}"] = st.radio(f"Q{i + 1}. {q['question']}", q["options"], key=f"{section_key}_radio_{i}", index=None)
# Technical
with st.container(border=True):
    section_title("Technical Questions")
    for i, q in enumerate(interview.get("technical", [])):
        answers[f"tech_{i}"] = st.text_area(f"Q{i + 1}. {q}", key=f"tech_answer_{i}")
    if interview.get("coding_question"):
        section_heading("Coding Question")
        st.code(interview["coding_question"], language=None)
        answers["coding"] = st.text_area("Your solution", key="coding_answer", height=180)
st.session_state["interview_answers"] = answers
col1, col2 = st.columns(2)
with col1:
    if st.button("Back", use_container_width=True, key="btn_back_interview"):
        st.switch_page("pages/results.py")
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
    divider()
    with st.container(border=True):
        st.markdown(circular_score(evaluation.get("overall_score", 0), "Overall Score"), unsafe_allow_html=True)
    status_class = 'good' if evaluation.get('readiness_level') in ('Ready', 'Highly Ready') else 'warn'
    status_banner(f"Readiness Level: {evaluation.get('readiness_level', '-')}", status_class)
    with st.container(border=True):
        cat = evaluation.get("category_scores", {})
        cats = st.columns(5)
        for col, (key, label) in zip(cats, [("aptitude", "≡ƒº« Aptitude"), ("verbal", "≡ƒùú∩╕Å Verbal"), ("reasoning", "≡ƒº⌐ Reasoning"), ("technical", "≡ƒ¢á∩╕Å Technical"), ("coding", "≡ƒÆ╗ Coding")]):
            with col:
                val = cat.get(key)
                st.metric(label, f"{val}%" if val is not None else "N/A")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<strong>Strong Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("strong_areas", [])), unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown("<strong>Weak Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("weak_areas", [])), unsafe_allow_html=True)
    if st.button("Continue to Mini Mock Interview", type="primary", key="btn_interview_to_mock"):
        st.switch_page("pages/mock_interview.py")
# Page 5b ΓÇö Mini Mock Interview


