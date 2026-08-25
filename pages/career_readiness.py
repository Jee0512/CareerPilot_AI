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
    render_step_track, render_page_header,
    render_section_title, render_badge_list, render_circular_score, render_job_card
)

def render_local_success_gradient(emoji: str, title: str, message: str):
    """Render text with a success gradient in the new foundation."""
    st.html(f'''
    <div class="cp-ui" style="background: linear-gradient(135deg, var(--cp-color-success-bg) 0%, rgba(16, 185, 129, 0.05) 100%); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: var(--cp-radius-lg); padding: var(--cp-space-xl); text-align: center; margin-bottom: var(--cp-space-xl);">
        <div style="font-size: 3rem; margin-bottom: var(--cp-space-md);">{emoji}</div>
        <h2 style="font-size: 1.5rem; font-weight: 700; color: var(--cp-color-success); margin-bottom: var(--cp-space-sm);">{title}</h2>
        <p style="font-size: 1rem; font-weight: 500; color: rgba(16, 185, 129, 0.8); line-height: 1.5;">{message}</p>
    </div>
    ''')

def render_local_mentor_card(emoji: str, title: str, message: str):
    """Render an AI Mentor tip card."""
    st.html(f'''
    <div class="cp-ui" style="background: linear-gradient(135deg, var(--cp-color-info-bg) 0%, rgba(59, 130, 246, 0.05) 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: var(--cp-radius-lg); padding: var(--cp-space-xl); text-align: center; margin-bottom: var(--cp-space-xl);">
        <div style="font-size: 3rem; margin-bottom: var(--cp-space-md);">{emoji}</div>
        <h2 style="font-size: 1.5rem; font-weight: 700; color: var(--cp-color-info); margin-bottom: var(--cp-space-sm);">{title}</h2>
        <p style="font-size: 1rem; font-weight: 500; color: rgba(59, 130, 246, 0.8); line-height: 1.5;">{message}</p>
    </div>
    ''')

def render_local_decision_card(icon: str, title: str, description: str):
    """Render a card for career decisions using .cp-ui."""
    st.html(f'''
    <div class="cp-ui" style="background: var(--cp-color-surface); border: 1px solid var(--cp-color-border); border-radius: var(--cp-radius-lg); padding: var(--cp-space-xl); text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; box-shadow: var(--cp-shadow-subtle); transition: transform 0.2s, box-shadow 0.2s;">
        <div style="width: 48px; height: 48px; border-radius: 50%; background: var(--cp-color-primary-light); color: var(--cp-color-primary); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: var(--cp-space-md);">
            {icon}
        </div>
        <h3 style="font-size: 1.125rem; font-weight: 700; color: var(--cp-color-text); margin-bottom: var(--cp-space-sm);">{title}</h3>
        <p style="font-size: 0.875rem; color: var(--cp-color-text-secondary); line-height: 1.5; margin-bottom: 0;">{description}</p>
    </div>
    ''')

def render_local_metric_value(label: str, value: str, color_hex: str = ""):
    """Render a single metric."""
    color_attr = f"color: {color_hex};" if color_hex else "color: var(--cp-color-text);"
    st.html(f'''
    <div class="cp-ui" style="background: var(--cp-color-surface-muted); border: 1px solid var(--cp-color-border); border-radius: var(--cp-radius-md); padding: var(--cp-space-md); text-align: center;">
        <div style="font-size: 2rem; font-weight: 800; {color_attr} margin-bottom: 4px;">{value}</div>
        <div style="font-size: 0.75rem; font-weight: 700; color: var(--cp-color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
    </div>
    ''')



render_page_header("AI Career Readiness Decision")
recalc = st.session_state["recalculated_match"]
if recalc is None:
    st.warning("Please run the Resume Optimization and Recalculate Score first.")
    if st.button("Go to Optimize", key="btn_cr_back_optimize"):
        st.switch_page("pages/resume_optimize.py")
st.stop()
optimized_score = recalc["match_score"]
missing_skills = recalc["missing_skills"]
if optimized_score >= ELIGIBILITY_THRESHOLD:
    # CASE 1: Score >= 75 — Premium Success Card
    render_local_success_gradient("🎉", "Congratulations!", "Your optimized resume demonstrates strong alignment with the selected job description.<br>You are now ready for the assessment.")
    # Two action cards
    c1, c2 = st.columns(2)
    with c1:
        render_local_decision_card("📋", "Take AI Assessment", "Evaluate your readiness using an AI-generated assessment personalized to your resume and target role.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Take AI Assessment", type="primary", use_container_width=True, key="btn_cr_assessment"):
            st.switch_page("pages/interview.py")
    with c2:
        render_local_decision_card("💼", "Find Better Matching Jobs", "Explore additional opportunities that match your optimized resume.")
        st.markdown("<br>", unsafe_allow_html=True)
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
    # CASE 2: Score < 75 — AI Mentor Card (never display rejection/negative)
    render_local_mentor_card("🧐", "Your resume has improved significantly", "But additional preparation is recommended before applying for this role.<br>Based on your resume and the selected job description, we have prepared two personalized paths to help you become interview-ready.")
    # Two action cards
    c1, c2 = st.columns(2)
    with c1:
        render_local_decision_card("🎯", "Improve My Skills", "Get a personalized 7-day learning plan and AI mini project tailored to close your skill gaps.")
        st.markdown("<br>", unsafe_allow_html=True)
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
        render_local_decision_card("💼", "Find Better Matching Jobs", "Discover roles that better match your current skills rather than the original target role.")
        st.markdown("<br>", unsafe_allow_html=True)
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
    st.divider()
    render_section_title("📚 Your 7-Day Personalized Learning Plan")
    with st.container(border=True):
        st.markdown(st.session_state["learning_plan_7day"])
    # Mini Project
    project = st.session_state["ai_mini_project"]
    if project:
        render_section_title("🚀 AI Mini Project Recommendation")
        with st.container(border=True):
            render_section_title(f"{project.get('title', 'AI Project')}")
            st.caption(f"{project.get('objective', '')}")
            meta = st.columns(3)
            with meta[0]:
                render_local_metric_value("Difficulty", project.get('difficulty', 'Intermediate'))
            with meta[1]:
                render_local_metric_value("Duration", project.get('estimated_duration', '1-2 weeks'))
            with meta[2]:
                render_local_metric_value("Skills Learned", str(len(project.get('skills_learned', []))))
            render_section_title("Features", size="1rem")
            for feat in project.get("features", []):
                st.markdown(f"- {feat}")
            render_section_title("Technologies", size="1rem")
            render_badge_list(project.get("technologies", []), "info")
            render_section_title("Skills You Will Develop", size="1rem")
            render_badge_list(project.get("skills_learned", []), "purple")
            st.markdown(f"<p style='color:var(--cp-color-text-muted);font-size:0.9rem;margin-top:0.75rem;'><strong>Expected Outcome:</strong> {project.get('expected_outcome', '')}</p>", unsafe_allow_html=True)
    # Career Progress Tracker - integrated into Improve My Skills workflow
    st.divider()
    render_section_title("📈 Career Progress Tracker")
    st.markdown("Upload your improved resume after completing the learning plan to see your progress.")
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
            render_section_title("Progress Dashboard")
            dash_cols = st.columns(4)
            with dash_cols[0]:
                render_local_metric_value("Previous Score", f"{optimized_score}%", "var(--cp-color-danger)")
            with dash_cols[1]:
                render_local_metric_value("Current Score", f"{imp['match_score']}%", "var(--cp-color-success)")
            with dash_cols[2]:
                sign = "+" if improvement_pct >= 0 else ""
                clr = "var(--cp-color-success)" if improvement_pct >= 0 else "var(--cp-color-danger)"
                render_local_metric_value("Improvement", f"{sign}{improvement_pct}%", clr)
            with dash_cols[3]:
                render_local_metric_value("New Skills", str(len(new_skills_added)), "var(--cp-color-info)")
            # Skills breakdown
            sk_col1, sk_col2, sk_col3 = st.columns(3)
            with sk_col1:
                if new_skills_added:
                    st.markdown("**🆕 New Skills Added:**")
                    render_badge_list(new_skills_added, "good")
            with sk_col2:
                if skills_improved:
                    st.markdown("**✅ Improved Skills:**")
                    render_badge_list(skills_improved, "info")
            with sk_col3:
                if remaining_missing:
                    st.markdown("**❌ Remaining Missing:**")
                    render_badge_list(remaining_missing, "bad")
            # AI Summary
            if st.session_state["improvement_summary"]:
                st.markdown(f"<div class='cp-ui' style='background:var(--cp-color-surface-muted);border:1px solid var(--cp-color-border);border-radius:var(--cp-radius-md);padding:var(--cp-space-md);margin-top:var(--cp-space-md);font-size:0.9rem;color:var(--cp-color-text-secondary);'><strong>🤖 AI Summary:</strong> {st.session_state['improvement_summary']}</div>", unsafe_allow_html=True)
        # Progress history chart
        if len(st.session_state["progress_history"]) > 0:
            with st.container(border=True):
                render_section_title("Progress History")
                hist = st.session_state["progress_history"]
                chart_data = {
                    "Attempt": [h["attempt"] for h in hist],
                    "Score": [h["new_score"] for h in hist],
                }
                st.line_chart(chart_data, x="Attempt", y="Score", height=200)
        # Check if ready for assessment
        if imp["match_score"] >= ELIGIBILITY_THRESHOLD:
            render_local_success_gradient("🎉", "Congratulations!", f"You are now interview-ready! Your resume score of {imp['match_score']}% meets the assessment threshold.")
            if st.button("Unlock AI Assessment", type="primary", use_container_width=True, key="btn_unlock_assessment"):
                st.switch_page("pages/interview.py")
        else:
            st.warning("Keep going! You're making great progress. Continue with the learning plan and try uploading another improved resume.")
            # Regenerate learning plan + mini project based on remaining missing skills
            if st.button("Regenerate Learning Plan", type="secondary", key="btn_regenerate_plan"):
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
    st.divider()
    render_section_title("💼 Recommended Jobs Based on Your Skills")
    for job in st.session_state["career_readiness_jobs"]:
        render_job_card(job, apply_key="apply_urls")
# Navigation buttons
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Optimize", use_container_width=True, key="btn_cr_back"):
        st.switch_page("pages/resume_optimize.py")
with col2:
    if st.button("Career Toolkit", use_container_width=True, key="btn_cr_toolkit"):
        st.switch_page("pages/toolkit.py")
# Page 4d ΓÇö Career Readiness Jobs (separate view)


