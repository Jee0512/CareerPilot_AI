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

from ui.icons import icon_upload, icon_zap, icon_brain, icon_target

render_top_navbar()
hero_col1, hero_col2 = st.columns([1.1, 1], gap="large")

with hero_col1:
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    # Hero Text wrapped in .cp-ui namespace
    st.html(f"""
    <div class="cp-ui">
        <span class="cp-badge-base cp-animate-in" style="background-color: var(--cp-color-info-bg); color: var(--cp-color-info); border-color: rgba(59, 130, 246, 0.2); margin-bottom: var(--cp-space-md);">
            ⚡ AI Resume Analyzer
        </span>
        <h1 class="cp-text-display cp-animate-in">
            Is your resume ready for<br>your <span style="color:var(--cp-color-primary);">dream job</span>?
        </h1>
        <p class="cp-text-body cp-animate-in" style="font-size: 1.15rem; max-width: 90%; margin-bottom: var(--cp-space-xl);">
            Check ATS compatibility, semantic matching, missing skills, interview readiness,
            and AI roadmap generation — all with a single click.
        </p>
    </div>
    """)
    
    # Premium Upload Card
    st.html(f"""
    <div class="cp-ui">
        <div class="cp-card-base cp-animate-in" style="border: 1px dashed var(--cp-color-border-strong); background: var(--cp-color-surface-muted); margin-bottom: var(--cp-space-sm);">
            <div style="color: var(--cp-color-primary); display: flex; justify-content: center; margin-bottom: var(--cp-space-md);">
                {icon_upload(size=48, stroke_width=1.5)}
            </div>
            <p class="cp-text-h3" style="margin-bottom: var(--cp-space-xs);">Upload your resume</p>
            <p class="cp-text-muted">Drag & drop your PDF or DOCX</p>
        </div>
    </div>
    """)
    
    # Inline uploader (Native Streamlit)
    uploaded_landing = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="landing_uploader", label_visibility="collapsed")
    if uploaded_landing is not None:
        try:
            with st.spinner("Analyzing your profile..."):
                fb = uploaded_landing.getvalue()
                is_pdf = uploaded_landing.name.lower().endswith(".pdf")
                text = extract_text_from_pdf(fb) if is_pdf else extract_text_from_docx(fb)
                skills = extract_skills(text)
            st.session_state["resume_text"] = text
            st.session_state["resume_skills"] = skills
            st.session_state["resume_file_type"] = "pdf" if is_pdf else "docx"
            st.session_state["resume_pdf_bytes"] = fb if is_pdf else None
            st.success(f"Resume parsed! Found {len(skills)} skills.")
            st.switch_page("pages/job_description.py")
        except RuntimeError as exc:
            st.error(str(exc))
    
    privacy_note()

with hero_col2:
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    
    # Dashboard preview glow wrapper
    st.html(f"""
    <div class="cp-ui" style="position: relative;">
        <div style="position: absolute; top: -10%; left: -10%; right: -10%; bottom: -10%; background: radial-gradient(circle at center, var(--cp-color-surface-inset) 0%, transparent 60%); z-index: 0; pointer-events: none;"></div>
        
        <div class="cp-card-base cp-animate-in" style="position: relative; z-index: 1; border-radius: 24px; box-shadow: var(--cp-shadow-large); text-align: left; padding: var(--cp-space-xl);">
            
            <div class="cp-flex-row" style="justify-content: space-between; margin-bottom: var(--cp-space-xl);">
                <div class="cp-flex-col" style="align-items: center;">
                    <div style="font-size:2.5rem; font-weight: 800; color:var(--cp-color-success); line-height: 1;">92</div>
                    <div style="font-size:0.75rem; font-weight: 600; color:var(--cp-color-text-muted); text-transform: uppercase; margin-top: 0.5rem; letter-spacing: 0.05em;">ATS Score</div>
                </div>
                <div style="width: 1px; height: 40px; background: var(--cp-color-border);"></div>
                <div class="cp-flex-col" style="align-items: center;">
                    <div style="font-size:2.5rem; font-weight: 800; color:var(--cp-color-primary); line-height: 1;">85</div>
                    <div style="font-size:0.75rem; font-weight: 600; color:var(--cp-color-text-muted); text-transform: uppercase; margin-top: 0.5rem; letter-spacing: 0.05em;">Match</div>
                </div>
                <div style="width: 1px; height: 40px; background: var(--cp-color-border);"></div>
                <div class="cp-flex-col" style="align-items: center;">
                    <div style="font-size:2.5rem; font-weight: 800; color:var(--cp-color-warning); line-height: 1;">78</div>
                    <div style="font-size:0.75rem; font-weight: 600; color:var(--cp-color-text-muted); text-transform: uppercase; margin-top: 0.5rem; letter-spacing: 0.05em;">Semantic</div>
                </div>
            </div>
            
            <div style="margin-bottom: var(--cp-space-lg);">
                <div class="cp-flex-row" style="justify-content: space-between; font-size: 0.85rem; color: var(--cp-color-text-secondary); margin-bottom: 0.4rem;">
                    <span>Keyword Match</span><span style="font-weight: 600; color: var(--cp-color-text);">88%</span>
                </div>
                <div style="background:var(--cp-color-surface-inset); border-radius:100px; height:8px; overflow:hidden;">
                    <div style="width:88%; background:var(--cp-color-primary); border-radius:100px; height:8px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: var(--cp-space-lg);">
                <div class="cp-flex-row" style="justify-content: space-between; font-size: 0.85rem; color: var(--cp-color-text-secondary); margin-bottom: 0.4rem;">
                    <span>Experience Relevance</span><span style="font-weight: 600; color: var(--cp-color-text);">82%</span>
                </div>
                <div style="background:var(--cp-color-surface-inset); border-radius:100px; height:8px; overflow:hidden;">
                    <div style="width:82%; background:var(--cp-color-success); border-radius:100px; height:8px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: var(--cp-space-xl);">
                <div class="cp-flex-row" style="justify-content: space-between; font-size: 0.85rem; color: var(--cp-color-text-secondary); margin-bottom: 0.4rem;">
                    <span>Education Alignment</span><span style="font-weight: 600; color: var(--cp-color-text);">70%</span>
                </div>
                <div style="background:var(--cp-color-surface-inset); border-radius:100px; height:8px; overflow:hidden;">
                    <div style="width:70%; background:var(--cp-color-warning); border-radius:100px; height:8px;"></div>
                </div>
            </div>
            
            <div class="cp-flex-row" style="gap: var(--cp-space-sm); flex-wrap: wrap;">
                <span class="cp-badge-base" style="background: var(--cp-color-info-bg); color: var(--cp-color-info); border-color: rgba(59, 130, 246, 0.2);">Python</span>
                <span class="cp-badge-base" style="background: var(--cp-color-info-bg); color: var(--cp-color-info); border-color: rgba(59, 130, 246, 0.2);">TensorFlow</span>
                <span class="cp-badge-base" style="background: var(--cp-color-success-bg); color: var(--cp-color-success); border-color: rgba(16, 185, 129, 0.2);">Docker</span>
                <span class="cp-badge-base" style="background: var(--cp-color-danger-bg); color: var(--cp-color-danger); border-color: rgba(239, 68, 68, 0.2);">Kubernetes</span>
            </div>
        </div>
    </div>
    """)
    
    # Feature cards row
    st.html(f"""
    <div class="cp-ui" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--cp-space-md); margin-top: var(--cp-space-lg); animation: cp-fade-in-up 0.6s 0.2s ease-out both;">
        <div class="cp-card-base" style="padding: var(--cp-space-md);">
            <div style="color: var(--cp-color-primary); margin-bottom: var(--cp-space-sm); display: flex; justify-content: center;">
                {icon_zap(size=28)}
            </div>
            <div style="font-size:0.75rem; font-weight:600; color:var(--cp-color-text);">Instant Analysis</div>
        </div>
        <div class="cp-card-base" style="padding: var(--cp-space-md);">
            <div style="color: var(--cp-color-primary); margin-bottom: var(--cp-space-sm); display: flex; justify-content: center;">
                {icon_brain(size=28)}
            </div>
            <div style="font-size:0.75rem; font-weight:600; color:var(--cp-color-text);">AI Suggestions</div>
        </div>
        <div class="cp-card-base" style="padding: var(--cp-space-md);">
            <div style="color: var(--cp-color-primary); margin-bottom: var(--cp-space-sm); display: flex; justify-content: center;">
                {icon_target(size=28)}
            </div>
            <div style="font-size:0.75rem; font-weight:600; color:var(--cp-color-text);">Smart Matching</div>
        </div>
    </div>
    """)
