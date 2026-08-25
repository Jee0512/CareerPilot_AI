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


section_heading("AI Career Readiness Decision")
recalc = st.session_state["recalculated_match"]
if recalc is None:
    st.warning("Please run the Resume Optimization and Recalculate Score first.")
    if st.button("Go to Optimize", key="btn_cr_back_optimize"):
        st.switch_page("pages/resume_optimize.py")
st.stop()
optimized_score = recalc["match_score"]
missing_skills = recalc["missing_skills"]
if optimized_score >= ELIGIBILITY_THRESHOLD:
    # CASE 1: Score >= 75 ΓÇö Premium Success Card
    success_gradient("≡ƒÄë", "Congratulations!", "Your optimized resume demonstrates strong alignment with the selected job description.<br>You are now ready for the assessment.")
    # Two action cards
    c1, c2 = st.columns(2)
    with c1:
        decision_card("≡ƒôï", "Take AI Assessment", "Evaluate your readiness using an AI-generated assessment personalized to your resume and target role.", "#EEF4FF", "cp-animate-in-left")
        if st.button("Take AI Assessment", type="primary", use_container_width=True, key="btn_cr_assessment"):
            st.switch_page("pages/interview.py")
    with c2:
        decision_card("≡ƒÆ╝", "Find Better Matching Jobs", "Explore additional opportunities that match your optimized resume.", "#FEF3C7", "cp-animate-in-right")
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
                st.switch_page("pages/career_readiness_jobs.py")
else:
    # CASE 2: Score < 75 ΓÇö AI Mentor Card (never display rejection/negative)
    mentor_card("≡ƒº¡", "Your resume has improved significantly", "But additional preparation is recommended before applying for this role.<br>Based on your resume and the selected job description, we have prepared two personalized paths to help you become interview-ready.")
    # Two action cards
    c1, c2 = st.columns(2)
    with c1:
        decision_card("≡ƒÄ»", "Improve My Skills", "Get a personalized 7-day learning plan and AI mini project tailored to close your skill gaps.", "#EDE9FE", "cp-animate-in-left")
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
        decision_card("≡ƒÆ╝", "Find Better Matching Jobs", "Discover roles that better match your current skills rather than the original target role.", "#FEF3C7", "cp-animate-in-right")
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
                st.switch_page("pages/career_readiness_jobs.py")
# Show learning plan and mini project if generated
if st.session_state["learning_plan_7day"]:
    divider()
    section_heading("≡ƒôÜ Your 7-Day Personalized Learning Plan")
    with st.container(border=True):
        st.markdown(st.session_state["learning_plan_7day"])
    # Mini Project
    project = st.session_state["ai_mini_project"]
    if project:
        section_heading("≡ƒÜÇ AI Mini Project Recommendation")
        with st.container(border=True):
            section_heading("{project.get('title', 'AI Project')}")
            st.caption("{project.get('objective', '')}")
            meta = st.columns(3)
            with meta[0]:
                metric_value("Difficulty", project.get('difficulty', 'Intermediate'))
            with meta[1]:
                metric_value("Duration", project.get('estimated_duration', '1-2 weeks'))
            with meta[2]:
                metric_value("Skills Learned", str(len(project.get('skills_learned', []))))
            section_heading("Features")
            for feat in project.get("features", []):
                st.markdown(f"- {feat}")
            section_heading("Technologies")
            badge_list(project.get("technologies", []), "info")
            section_heading("Skills You Will Develop")
            badge_list(project.get("skills_learned", []), "purple")
            st.markdown(f"<p style='color:#6B7280;font-size:0.9rem;margin-top:0.75rem;'><strong>Expected Outcome:</strong> {project.get('expected_outcome', '')}</p>", unsafe_allow_html=True)
    # Career Progress Tracker - integrated into Improve My Skills workflow
    divider()
    section_heading("≡ƒôê Career Progress Tracker", "Upload your improved resume after completing the learning plan to see your progress.")
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
        with st.container(border=True):
            section_title("Progress Dashboard")
            dash_cols = st.columns(4)
            with dash_cols[0]:
                metric_value("Previous Score", f"{optimized_score}%", "#EF4444")
            with dash_cols[1]:
                metric_value("Current Score", f"{imp['match_score']}%", "#10B981")
            with dash_cols[2]:
                sign = "+" if improvement_pct >= 0 else ""
                clr = "#10B981" if improvement_pct >= 0 else "#EF4444"
                metric_value("Improvement", f"{sign}{improvement_pct}%", clr)
            with dash_cols[3]:
                metric_value("New Skills", str(len(new_skills_added)), "#2563EB")
            # Skills breakdown
            sk_col1, sk_col2, sk_col3 = st.columns(3)
            with sk_col1:
                if new_skills_added:
                    st.markdown("**≡ƒåò New Skills Added:** " + " ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in new_skills_added), unsafe_allow_html=True)
            with sk_col2:
                if skills_improved:
                    st.markdown("**Γ£à Improved Skills:** " + " ".join(f"<span class='cp-badge cp-badge-info'>{s}</span>" for s in skills_improved), unsafe_allow_html=True)
            with sk_col3:
                if remaining_missing:
                    st.markdown("**Γ¥î Remaining Missing:** " + " ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in remaining_missing), unsafe_allow_html=True)
            # AI Summary
            if st.session_state["improvement_summary"]:
                st.markdown(f"<div style='background:#F8FAFC;border-radius:12px;padding:1rem;margin-top:0.75rem;font-size:0.9rem;color:#374151;'><strong>≡ƒñû AI Summary:</strong> {st.session_state['improvement_summary']}</div>", unsafe_allow_html=True)
        # Progress history chart
        if len(st.session_state["progress_history"]) > 0:
            with st.container(border=True):
                section_heading("Progress History")
                hist = st.session_state["progress_history"]
                chart_data = {
                    "Attempt": [h["attempt"] for h in hist],
                    "Score": [h["new_score"] for h in hist],
                }
                st.line_chart(chart_data, x="Attempt", y="Score", height=200)
        # Check if ready for assessment
        if imp["match_score"] >= ELIGIBILITY_THRESHOLD:
            success_gradient("≡ƒÄë", "Congratulations!", f"You are now interview-ready! Your resume score of {imp['match_score']}% meets the assessment threshold.")
            if st.button("Unlock AI Assessment", type="primary", use_container_width=True, key="btn_unlock_assessment"):
                st.switch_page("pages/interview.py")
        else:
            status_banner("Keep going! You're making great progress. Continue with the learning plan and try uploading another improved resume.", "warn")
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
    divider()
    section_heading("≡ƒÆ╝ Recommended Jobs Based on Your Skills")
    for job in st.session_state["career_readiness_jobs"]:
        render_job_card(job, apply_key="apply_urls")
# Navigation buttons
divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Optimize", use_container_width=True, key="btn_cr_back"):
        st.switch_page("pages/resume_optimize.py")
with col2:
    if st.button("Career Toolkit", use_container_width=True, key="btn_cr_toolkit"):
        st.switch_page("pages/toolkit.py")
# Page 4d ΓÇö Career Readiness Jobs (separate view)


