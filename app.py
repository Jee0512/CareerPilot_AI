"""
CareerPilot AI — app.py
========================
Entry point. Run with:  streamlit run app.py

Seven-page flow controlled entirely via st.session_state["page"]:
  1. landing         5. interview
  2. upload_resume   6. jobs
  3. job_description 7. toolkit (outreach email / learning roadmap / report)
  4. results

All heavy imports (spaCy, sentence-transformers) happen inside modules/
and are cached with @st.cache_resource, so they only load once per session.
"""

import re
import streamlit as st
from dotenv import load_dotenv
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

load_dotenv()

st.set_page_config(page_title="CareerPilot AI", page_icon="🧭", layout="wide")

# ============================================================================
# Load external CSS, Tailwind CDN & reusable UI components
# ============================================================================
from pathlib import Path
from modules.ui_components import (
    inject_tailwind, render_top_navbar, render_step_track, circular_score,
    STEP_SEQUENCE, STEP_LABELS,
    section_heading, section_title,
    card_open, card_close,
    status_banner, privacy_note,
    badge_list, labeled_badges,
    metric_value, score_comparison,
    render_job_card, compare_grid,
    decision_card, success_gradient, mentor_card,
    divider,
)

_CSS_PATH = Path(__file__).parent / "assets" / "style.css"
_CUSTOM_CSS = _CSS_PATH.read_text(encoding="utf-8")
st.markdown(f"<style>{_CUSTOM_CSS}</style>", unsafe_allow_html=True)
inject_tailwind()

# ----------------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------------
DEFAULT_STATE = {
    "page": "landing",
    "resume_text": None,
    "resume_skills": [],
    "resume_file_type": None,
    "jd_text": "",
    "match_result": None,
    "interview": None,
    "interview_answers": {},
    "evaluation": None,
    "recommended_jobs": None,
    "outreach_email": None,
    "learning_roadmap": None,
    "bullet_rewrites": None,
    "tailored_resume": None,
    "resume_diff_html": None,
    "section_diffs": None,
    "resume_pdf_bytes": None,
    "resume_layout_lines": None,
    "layout_rewrites": None,
    "optimized_pdf_bytes": None,
    "optimized_resume_text": None,
    "recalculated_match": None,
    "resume_debate": None,
    "mock_interview_questions": None,
    "mock_interview_answers": {},
    "mock_interview_evaluation": None,
    "company_name": "",
    "company_url": "",
    "company_context": "",
    # Career Readiness Decision Engine state
    "career_readiness_shown": False,
    "learning_plan_7day": None,
    "ai_mini_project": None,
    "improved_resume_text": None,
    "improved_resume_score": None,
    "improvement_summary": None,
    "career_readiness_jobs": None,
    "progress_history": [],
    "previous_resume_skills": [],
    "career_readiness_origin": None,
}
for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Sync query params with session state for browser Back/Forward support
current_view = st.query_params.get("view", "landing")
if st.session_state.get("page") != current_view:
    st.session_state["page"] = current_view


def goto(page: str):
    st.session_state["page"] = page
    st.query_params["view"] = page
    st.rerun()


def reset_all():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value
    st.rerun()


# ============================================================================
# Page — Landing
# ============================================================================
def page_landing():
    render_top_navbar()
    hero_col1, hero_col2 = st.columns([1.1, 1])

    with hero_col1:
        st.markdown('<span class="cp-animate-in cp-badge cp-badge-info">AI Resume Analyzer</span>', unsafe_allow_html=True)
        st.markdown('<h1 class="cp-animate-in" style="font-size:2.8rem;line-height:1.15;margin-bottom:1rem;">Is your resume ready for<br>your <span style="color:var(--cp-primary);">dream job</span>?</h1>', unsafe_allow_html=True)
        st.markdown("""
        <p class="cp-animate-in text-base leading-relaxed text-gray-500 mb-6">
        Check ATS compatibility, semantic matching, missing skills, interview readiness,
        personalized quizzes, and AI roadmap generation — all in one place.
        </p>
        """, unsafe_allow_html=True)

        # Premium Upload Card
        st.markdown("""
        <div class='cp-card cp-card-glass' style='border-radius:24px;text-align:center;padding:2rem;margin-bottom:0.5rem;'>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--cp-primary)" stroke-width="1.5" style="margin-bottom:0.75rem;">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p class="font-semibold text-gray-900 mb-2">Upload your resume to get started</p>
            <p class="text-xs text-gray-400 mb-4">PDF or DOCX &middot; Free &middot; No sign-up required</p>
        </div>
        """, unsafe_allow_html=True)

        # Inline uploader
        uploaded_landing = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="landing_uploader", label_visibility="collapsed")
        if uploaded_landing is not None:
            try:
                with st.spinner("Reading your resume..."):
                    fb = uploaded_landing.getvalue()
                    is_pdf = uploaded_landing.name.lower().endswith(".pdf")
                    text = extract_text_from_pdf(fb) if is_pdf else extract_text_from_docx(fb)
                    skills = extract_skills(text)
                st.session_state["resume_text"] = text
                st.session_state["resume_skills"] = skills
                st.session_state["resume_file_type"] = "pdf" if is_pdf else "docx"
                st.session_state["resume_pdf_bytes"] = fb if is_pdf else None
                st.success(f"Resume parsed! Found {len(skills)} skills.")
                goto("job_description")
            except RuntimeError as exc:
                st.error(str(exc))

        privacy_note()

    with hero_col2:
        # Dashboard preview
        st.markdown("""
        <div class='cp-card' style='padding:1.5rem;animation:slideInRight 0.6s ease forwards;'>
            <div class="flex justify-between items-center mb-4">
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:var(--cp-success);">92</div>
                    <div class="cp-metric-label">ATS Score</div>
                </div>
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:var(--cp-primary);">85</div>
                    <div class="cp-metric-label">Skill Match</div>
                </div>
                <div class="cp-metric">
                    <div class="cp-metric-value" style="font-size:2.2rem;color:var(--cp-warning);">78</div>
                    <div class="cp-metric-label">Semantic</div>
                </div>
            </div>
            <div class="mb-3">
                <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Keyword Match</span><span class="font-semibold text-gray-900">88%</span>
                </div>
                <div style="background:var(--cp-border);border-radius:var(--cp-radius-full);height:8px;overflow:hidden;">
                    <div style="width:88%;background:var(--cp-primary);border-radius:var(--cp-radius-full);height:8px;"></div>
                </div>
            </div>
            <div class="mb-3">
                <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Experience Relevance</span><span class="font-semibold text-gray-900">82%</span>
                </div>
                <div style="background:var(--cp-border);border-radius:var(--cp-radius-full);height:8px;overflow:hidden;">
                    <div style="width:82%;background:var(--cp-success);border-radius:var(--cp-radius-full);height:8px;"></div>
                </div>
            </div>
            <div class="mb-4">
                <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Education Alignment</span><span class="font-semibold text-gray-900">70%</span>
                </div>
                <div style="background:var(--cp-border);border-radius:var(--cp-radius-full);height:8px;overflow:hidden;">
                    <div style="width:70%;background:var(--cp-warning);border-radius:var(--cp-radius-full);height:8px;"></div>
                </div>
            </div>
            <div class="flex gap-2 flex-wrap">
                <span class="cp-badge cp-badge-good">Python</span>
                <span class="cp-badge cp-badge-info">TensorFlow</span>
                <span class="cp-badge cp-badge-purple">Docker</span>
                <span class="cp-badge cp-badge-bad">Kubernetes</span>
                <span class="cp-badge cp-badge-warn">SQL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards row
        st.markdown("""
        <div class="grid grid-cols-3 gap-3 mt-4 cp-animate-in">
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div class="text-2xl mb-1">&#9889;</div>
                <div class="text-xs font-semibold text-gray-900">Instant Analysis</div>
            </div>
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div class="text-2xl mb-1">&#129302;</div>
                <div class="text-xs font-semibold text-gray-900">AI Suggestions</div>
            </div>
            <div class="cp-card" style="padding:1rem;text-align:center;">
                <div class="text-2xl mb-1">&#127919;</div>
                <div class="text-xs font-semibold text-gray-900">Smart Matching</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # Page 2 — Resume Upload

# ============================================================================
# Page — Upload Resume
# ============================================================================
def page_upload_resume():
    render_step_track("upload_resume")
    section_heading("Upload Your Resume", "Start by uploading your resume in PDF or DOCX format.")

    card_open(extra_style="padding:2rem;")
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
            st.success(f"Resume parsed — found {len(skills)} recognizable skills.")
            if not is_pdf:
                st.caption("Note: layout-preserving optimization (exact design edit) is only available for PDF uploads.")
            if skills:
                badge_list(skills, "good")
        except RuntimeError as exc:
            st.error(str(exc))
    elif st.session_state["resume_text"]:
        st.info("A resume is already loaded. Upload a new file to replace it.")
    card_close()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_upload"):
            goto("landing")
    with col2:
        can_continue = st.session_state["resume_text"] is not None
        if st.button("Continue", use_container_width=True, type="primary", disabled=not can_continue, key="btn_continue_upload"):
            goto("job_description")


    # Page 3 — Job Description Input

# ============================================================================
# Page — Job Description
# ============================================================================
def page_job_description():
    render_step_track("job_description")
    section_heading("Job Description Source", "Provide the job description in one of three ways.")

    tab_paste, tab_upload, tab_url = st.tabs(["Paste Job Description", "Upload File", "Job URL"])

    with tab_paste:
        card_open()
        jd_text = st.text_area(
            "Paste the job description here", value=st.session_state["jd_text"], height=250,
            placeholder="Copy and paste the full job description...", key="jd_textarea_paste",
        )
        st.session_state["jd_text"] = jd_text
        card_close()

    with tab_upload:
        card_open()
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
        card_close()

    with tab_url:
        card_open()
        st.markdown('<p class="text-sm text-gray-500 mb-3">Supported: LinkedIn, Indeed, Naukri, Company Careers pages</p>', unsafe_allow_html=True)
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
                    status_banner(f"{exc}<br><br>Automatic extraction isn't supported for every site (many require login). Try pasting the text manually instead.", "warn")

        if st.session_state["jd_text"]:
            st.session_state["jd_text"] = st.text_area(
                "Extracted text (editable)", value=st.session_state["jd_text"], height=200, key="jd_url_result_2",
            )
        card_close()

    jd_text = st.session_state["jd_text"]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_jd"):
            goto("upload_resume")
    with col2:
        if st.button("Analyze Resume", use_container_width=True, type="primary", disabled=not jd_text.strip(), key="btn_analyze_jd"):
            try:
                with st.spinner("Comparing your resume against the job description..."):
                    result = compute_match(st.session_state["resume_text"], jd_text)
                st.session_state["match_result"] = result
                goto("results")
            except Exception as exc:
                st.error(f"Something went wrong while analyzing: {exc}")


    # Page 4 — Results Dashboard

# ============================================================================
# Page — Results
# ============================================================================
def page_results():
    render_step_track("results")
    section_heading("Results Dashboard")
    result = st.session_state["match_result"]
    if result is None:
        st.warning("No analysis yet — go back and provide a job description first.")
        if st.button("Back", key="btn_back_no_result"):
            goto("job_description")
    return

    score = result["match_score"]
    is_eligible = score >= ELIGIBILITY_THRESHOLD

    # Score + eligibility row
    score_col1, score_col2 = st.columns([1, 1.5])
    with score_col1:
        card_open(extra_style="display:flex;justify-content:center;padding:2rem;")
        st.markdown(circular_score(score, "Resume Match Score"), unsafe_allow_html=True)
        card_close()
    with score_col2:
        if is_eligible:
            status_banner("Eligible for Interview! Your resume meets the 75%+ match threshold for this role.", "good")
        else:
            status_banner("Not yet eligible for interview (below 75%). Optimize your resume or explore better-fitting roles below.", "bad")
        
        card_open()
        metric_row = st.columns(3)
        with metric_row[0]:
            st.metric("Match Score", f"{score}%")
        with metric_row[1]:
            st.metric("Skills Matched", len(result["matched_skills"]))
        with metric_row[2]:
            st.metric("Skills Missing", len(result["missing_skills"]))
        card_close()

    # Skills breakdown
    col1, col2 = st.columns(2)
    with col1:
        card_open()
        section_title("Matching Skills")
        st.progress(min(1.0, result["matched_pct"] / 100))
        if result["matched_skills"]:
            badge_list(result["matched_skills"], "good")
        else:
            st.caption("No overlapping skills detected.")
        card_close()
    with col2:
        card_open()
        section_title("Missing Skills")
        st.progress(min(1.0, result["missing_pct"] / 100))
        if result["missing_skills"]:
            badge_list(result["missing_skills"], "bad")
        else:
            st.caption("No missing skills detected!")
        card_close()

    # AI Resume Debate
    card_open()
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
    card_close()

    # Next steps
    divider()
    section_heading("What would you like to do next?")

    opt1, opt2 = st.columns(2)
    with opt1:
        card_open(extra_style="text-align:center;")
        st.markdown("### Optimize Resume")
        st.caption("Get AI-powered rewrites tailored to this job description")
        if st.button("Optimize My Resume", use_container_width=True, type="primary", key="btn_option1"):
            goto("resume_optimize")
        card_close()
    with opt2:
        card_open(extra_style="text-align:center;")
        st.markdown("### Find Better Jobs")
        st.caption("Discover roles that better match your current skills")
        if st.button("Find Matching Jobs", use_container_width=True, key="btn_option2"):
            goto("jobs")
        card_close()

    if is_eligible:
        card_open(extra_classes="text-center")
        if st.button("Start AI Assessment", key="btn_direct_assessment"):
            goto("interview")
        card_close()

    if st.button("Back", key="btn_back_results"):
        goto("job_description")


    # Page 4b — AI Resume Optimizer + Before vs After Comparison

# ============================================================================
# Page — Resume Optimize
# ============================================================================
def page_resume_optimize():
    render_step_track("resume_optimize")
    section_heading("Optimize & Compare")

    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_optimize"):
            goto("results")
    return

    is_pdf_origin = st.session_state.get("resume_file_type") == "pdf" and st.session_state["resume_pdf_bytes"]

    # Step 1: Generate optimization
    if st.session_state["optimized_pdf_bytes"] is None:
        card_open(extra_style="text-align:center;padding:2rem;")
        st.markdown("### Ready to optimize?")
        st.caption("The AI will rewrite your resume content while preserving the exact original layout and design.")
        
        if st.button("Generate Optimized Resume", type="primary", key="btn_gen_optimized"):
            try:
                if is_pdf_origin:
                    with st.spinner("Analyzing layout and rewriting content..."):
                        lines = extract_layout_lines(st.session_state["resume_pdf_bytes"])
                        rewrites = generate_layout_constrained_rewrites(lines, st.session_state["jd_text"], result["matched_skills"], result["missing_skills"])
                        if not rewrites:
                            st.warning("No lines could be safely improved. Try a different job description, or your resume is already well-optimized.")
                            return
                        edited_pdf = apply_layout_preserving_edits(st.session_state["resume_pdf_bytes"], lines, rewrites)
                        optimized_text = lines_to_text(lines, rewrites)
                        original_text = lines_to_text(lines)
                        diff_html = build_resume_diff_html(original_text, optimized_text)
                        section_diffs = build_section_diffs(lines, rewrites)
                    st.session_state["resume_layout_lines"] = lines
                    st.session_state["layout_rewrites"] = rewrites
                    st.session_state["optimized_pdf_bytes"] = edited_pdf
                    st.session_state["optimized_resume_text"] = optimized_text
                    st.session_state["resume_diff_html"] = diff_html
                    st.session_state["section_diffs"] = section_diffs
                    st.success(f"Optimized {len(rewrites)} line(s) while keeping your original design.")
                else:
                    with st.spinner("Rewriting your resume content..."):
                        tailored = generate_tailored_resume(st.session_state["resume_text"], st.session_state["jd_text"], result["matched_skills"], result["missing_skills"])
                        diff_html = build_resume_diff_html(st.session_state["resume_text"], tailored)
                        pdf_bytes = build_resume_pdf(tailored)
                    st.session_state["optimized_resume_text"] = tailored
                    st.session_state["resume_diff_html"] = diff_html
                    st.session_state["optimized_pdf_bytes"] = pdf_bytes
                    st.success("Resume content optimized.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        
        if st.button("Back", key="btn_back_optimize_pre"):
            goto("results")
        card_close()
    return

    # Step 2: Show Before vs After comparison (MUST appear before download)
    section_heading("Before vs After Comparison", "Review the changes the AI made to your resume, section by section.")

    # Two-panel diff view
    section_diffs = st.session_state.get("section_diffs")
    if section_diffs:
        for sec in section_diffs:
            section_heading("{sec['name']}")
            if sec["changed"] and sec["diff_html"]:
                compare_grid(sec['diff_html'], sec['diff_html'])
            else:
                st.caption("No changes in this section.")
    else:
        # Fallback: show the full diff
        card_open(extra_classes="cp-compare-grid")
        st.markdown(f"""
        <div class="cp-compare-original">
            <div class="cp-compare-label">Original Content (Red = Removed)</div>
            <div style="font-size:0.85rem;line-height:1.5;">{st.session_state['resume_diff_html']}</div>
        </div>
        <div class="cp-compare-optimized">
            <div class="cp-compare-label">Optimized Content (Green = Added)</div>
            <div style="font-size:0.85rem;line-height:1.5;">{st.session_state['resume_diff_html']}</div>
        </div>
        """, unsafe_allow_html=True)
        card_close()

    # Step 3: PDF Preview
    divider()
    section_title("PDF Preview")
    b64_pdf = base64.b64encode(st.session_state["optimized_pdf_bytes"]).decode()
    st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" style="border-radius:12px;border:1px solid #E5E7EB;"></iframe>', unsafe_allow_html=True)

    # Step 4: Download options (AFTER comparison)
    divider()
    card_open()
    section_title("Download Optimized Resume", size="1.25rem")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button("Download as PDF (design preserved)", data=st.session_state["optimized_pdf_bytes"],
            file_name="optimized_resume.pdf", mime="application/pdf", key="btn_download_pdf",)
    with dcol2:
        st.download_button("Download as DOCX (text only)", data=build_resume_docx(st.session_state["optimized_resume_text"]),
            file_name="optimized_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_download_docx",)
    st.caption("The PDF preserves your exact original design. The DOCX is a clean text re-export.")
    card_close()

    # Step 5: Recalculate score - IMPROVED with score comparison
    card_open()
    section_title("Recalculate Match Score", size="1.25rem")
    if st.button("Recalculate Score", key="btn_recalculate"):
        try:
            with st.spinner("Recalculating..."):
                recalculated = compute_match(st.session_state["optimized_resume_text"], st.session_state["jd_text"])
            st.session_state["recalculated_match"] = recalculated
            st.session_state["previous_resume_skills"] = st.session_state["resume_skills"][:]
            st.rerun()
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")

    if st.session_state["recalculated_match"]:
        recalc = st.session_state["recalculated_match"]
        orig_score = st.session_state["match_result"]["match_score"] if st.session_state["match_result"] else 0

        # Premium score comparison dashboard
        score_comparison(orig_score, recalc['match_score'])

        # Matched & Missing skills badges
        st.markdown("<div style='margin:0.75rem 0;'>", unsafe_allow_html=True)
        if recalc["matched_skills"]:
            labeled_badges("✅ Matched Skills:", recalc["matched_skills"], "good")
        if recalc["missing_skills"]:
            st.markdown("<br>", unsafe_allow_html=True)
            labeled_badges("❌ Still Missing:", recalc["missing_skills"], "bad")
        card_close()

        if recalc["match_score"] >= ELIGIBILITY_THRESHOLD:
            status_banner("🎉 Your optimized resume now meets the assessment threshold!", "good")
        else:
            status_banner("Your resume has improved! Additional preparation is recommended before the assessment.", "warn")

    card_close()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_optimize"):
            goto("results")
    with col2:
        if st.session_state["recalculated_match"]:
            if st.button("Continue to Career Readiness", use_container_width=True, type="primary", key="btn_optimize_to_readiness"):
                st.session_state["career_readiness_shown"] = False
                goto("career_readiness")
        else:
            st.button("Continue", use_container_width=True, type="primary", disabled=True, key="btn_optimize_disabled")


    # Page 4c — AI Career Readiness Decision Engine

# ============================================================================
# Page — Career Readiness
# ============================================================================
def page_career_readiness():
    section_heading("AI Career Readiness Decision")

    recalc = st.session_state["recalculated_match"]
    if recalc is None:
        st.warning("Please run the Resume Optimization and Recalculate Score first.")
        if st.button("Go to Optimize", key="btn_cr_back_optimize"):
            goto("resume_optimize")
    return

    optimized_score = recalc["match_score"]
    missing_skills = recalc["missing_skills"]

    if optimized_score >= ELIGIBILITY_THRESHOLD:
        # CASE 1: Score >= 75 — Premium Success Card
        success_gradient("🎉", "Congratulations!", "Your optimized resume demonstrates strong alignment with the selected job description.<br>You are now ready for the assessment.")

        # Two action cards
        c1, c2 = st.columns(2)
        with c1:
            decision_card("📋", "Take AI Assessment", "Evaluate your readiness using an AI-generated assessment personalized to your resume and target role.", "#EEF4FF", "cp-animate-in-left")
            if st.button("Take AI Assessment", type="primary", use_container_width=True, key="btn_cr_assessment"):
                goto("interview")

        with c2:
            decision_card("💼", "Find Better Matching Jobs", "Explore additional opportunities that match your optimized resume.", "#FEF3C7", "cp-animate-in-right")
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
                    goto("career_readiness_jobs")

    else:
        # CASE 2: Score < 75 — AI Mentor Card (never display rejection/negative)
        mentor_card("🧭", "Your resume has improved significantly", "But additional preparation is recommended before applying for this role.<br>Based on your resume and the selected job description, we have prepared two personalized paths to help you become interview-ready.")

        # Two action cards
        c1, c2 = st.columns(2)
        with c1:
            decision_card("🎯", "Improve My Skills", "Get a personalized 7-day learning plan and AI mini project tailored to close your skill gaps.", "#EDE9FE", "cp-animate-in-left")
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
            decision_card("💼", "Find Better Matching Jobs", "Discover roles that better match your current skills rather than the original target role.", "#FEF3C7", "cp-animate-in-right")
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
                    goto("career_readiness_jobs")

    # Show learning plan and mini project if generated
    if st.session_state["learning_plan_7day"]:
        divider()
        section_heading("📚 Your 7-Day Personalized Learning Plan")
        card_open()
        st.markdown(st.session_state["learning_plan_7day"])
        card_close()

        # Mini Project
        project = st.session_state["ai_mini_project"]
        if project:
            section_heading("🚀 AI Mini Project Recommendation")
            card_open()
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
            card_close()

        # Career Progress Tracker - integrated into Improve My Skills workflow
        divider()
        section_heading("📈 Career Progress Tracker", "Upload your improved resume after completing the learning plan to see your progress.")

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
            card_open(extra_classes="cp-progress-dashboard")
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
                    st.markdown("**🆕 New Skills Added:** " + " ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in new_skills_added), unsafe_allow_html=True)
            with sk_col2:
                if skills_improved:
                    st.markdown("**✅ Improved Skills:** " + " ".join(f"<span class='cp-badge cp-badge-info'>{s}</span>" for s in skills_improved), unsafe_allow_html=True)
            with sk_col3:
                if remaining_missing:
                    st.markdown("**❌ Remaining Missing:** " + " ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in remaining_missing), unsafe_allow_html=True)

            # AI Summary
            if st.session_state["improvement_summary"]:
                st.markdown(f"<div style='background:#F8FAFC;border-radius:12px;padding:1rem;margin-top:0.75rem;font-size:0.9rem;color:#374151;'><strong>🤖 AI Summary:</strong> {st.session_state['improvement_summary']}</div>", unsafe_allow_html=True)

            card_close()

            # Progress history chart
            if len(st.session_state["progress_history"]) > 0:
                card_open()
                section_heading("Progress History")
                hist = st.session_state["progress_history"]
                chart_data = {
                    "Attempt": [h["attempt"] for h in hist],
                    "Score": [h["new_score"] for h in hist],
                }
                st.line_chart(chart_data, x="Attempt", y="Score", height=200)
                card_close()

            # Check if ready for assessment
            if imp["match_score"] >= ELIGIBILITY_THRESHOLD:
                success_gradient("🎉", "Congratulations!", f"You are now interview-ready! Your resume score of {imp['match_score']}% meets the assessment threshold.")
                if st.button("Unlock AI Assessment", type="primary", use_container_width=True, key="btn_unlock_assessment"):
                    goto("interview")
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
        section_heading("💼 Recommended Jobs Based on Your Skills")
        for job in st.session_state["career_readiness_jobs"]:
            render_job_card(job, apply_key="apply_urls")

    # Navigation buttons
    divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Optimize", use_container_width=True, key="btn_cr_back"):
            goto("resume_optimize")
    with col2:
        if st.button("Career Toolkit", use_container_width=True, key="btn_cr_toolkit"):
            goto("toolkit")


    # Page 4d — Career Readiness Jobs (separate view)

# ============================================================================
# Page — Career Readiness Jobs
# ============================================================================
def page_career_readiness_jobs():
    section_heading("💼 Recommended Jobs")
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
                goto("career_readiness")
    return

    for job in st.session_state["career_readiness_jobs"]:
        card_open()
        title_company = job.get("job_title", "Role")
        if job.get("company"):
            title_company += f" at {job['company']}"
        section_heading("{title_company}")
        st.markdown(f"**Estimated Match:** {job.get('estimated_match_pct', '-')}%")
        st.progress(min(1.0, (job.get("estimated_match_pct") or 0) / 100))
        st.caption(job.get("reason", ""))
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-good'>{s}</span>" for s in job.get("skills_present", [])), unsafe_allow_html=True)
        st.markdown(" ".join(f"<span class='cp-badge cp-badge-bad'>{s}</span>" for s in job.get("skills_missing", [])), unsafe_allow_html=True)
        urls = job.get("apply_urls", {})
        for site in ("LinkedIn", "Indeed", "Naukri", "Company Careers"):
            if site in urls:
                st.link_button(f"Apply on {site}", urls[site], use_container_width=True)
        card_close()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_crj_back"):
            goto("career_readiness")
    with col2:
        if st.button("Career Toolkit", use_container_width=True, key="btn_crj_toolkit"):
            goto("toolkit")


    # Page 5 — Interview Test

# ============================================================================
# Page — Interview
# ============================================================================
def page_interview():
    section_heading("Personalized Placement Assessment")

    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_interview_blocked"):
            goto("results")
    return

    effective_result = st.session_state["recalculated_match"] or result
    if effective_result["match_score"] < ELIGIBILITY_THRESHOLD:
        status_banner(f"Your current score ({effective_result['match_score']}%) is below the {ELIGIBILITY_THRESHOLD}% threshold required for the assessment.", "bad")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Optimize Resume", type="primary", key="btn_to_optimize"):
                goto("resume_optimize")
        with col2:
            if st.button("Find Better Jobs", key="btn_to_jobs"):
                goto("jobs")
    return

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
            goto("results")
    return

    interview = st.session_state["interview"]
    answers = st.session_state["interview_answers"]

    # MCQ sections in cards
    for section_key, section_title_text, icon in [("aptitude", "Aptitude", "🧮"), ("verbal", "Verbal Ability", "🗣️"), ("reasoning", "Logical Reasoning", "🧩")]:
        card_open()
        section_title(section_title_text, icon=icon)
        for i, q in enumerate(interview.get(section_key, [])):
            answers[f"{section_key}_{i}"] = st.radio(f"Q{i + 1}. {q['question']}", q["options"], key=f"{section_key}_radio_{i}", index=None)
        card_close()

    # Technical
    card_open()
    section_title("Technical Questions")
    for i, q in enumerate(interview.get("technical", [])):
        answers[f"tech_{i}"] = st.text_area(f"Q{i + 1}. {q}", key=f"tech_answer_{i}")
    if interview.get("coding_question"):
        section_heading("Coding Question")
        st.code(interview["coding_question"], language=None)
        answers["coding"] = st.text_area("Your solution", key="coding_answer", height=180)
    card_close()

    st.session_state["interview_answers"] = answers

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_interview"):
            goto("results")
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
        card_open(extra_style="display:flex;justify-content:center;")
        st.markdown(circular_score(evaluation.get("overall_score", 0), "Overall Score"), unsafe_allow_html=True)
        card_close()

        status_class = 'good' if evaluation.get('readiness_level') in ('Ready', 'Highly Ready') else 'warn'
        status_banner(f"Readiness Level: {evaluation.get('readiness_level', '-')}", status_class)

        card_open()
        cat = evaluation.get("category_scores", {})
        cats = st.columns(5)
        for col, (key, label) in zip(cats, [("aptitude", "🧮 Aptitude"), ("verbal", "🗣️ Verbal"), ("reasoning", "🧩 Reasoning"), ("technical", "🛠️ Technical"), ("coding", "💻 Coding")]):
            with col:
                val = cat.get(key)
                st.metric(label, f"{val}%" if val is not None else "N/A")
        card_close()

        c1, c2 = st.columns(2)
        with c1:
            card_open()
            st.markdown("<strong>Strong Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("strong_areas", [])), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open()
            st.markdown("<strong>Weak Areas</strong>" + "".join(f"<br>- {a}" for a in evaluation.get("weak_areas", [])), unsafe_allow_html=True)
            card_close()

        if st.button("Continue to Mini Mock Interview", type="primary", key="btn_interview_to_mock"):
            goto("mock_interview")


    # Page 5b — Mini Mock Interview

# ============================================================================
# Page — Mock Interview
# ============================================================================
def page_mock_interview():
    section_heading("Mini Mock Interview", "Answer each question as if in a real spoken interview.")

    if st.session_state["match_result"] is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_mock"):
            goto("results")
    return

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
            goto("interview")
    return

    questions = st.session_state["mock_interview_questions"]
    answers = st.session_state["mock_interview_answers"]

    for i, q in enumerate(questions):
        card_open()
        st.markdown(f"<strong>Q{i + 1}.</strong> {q}", unsafe_allow_html=True)
        card_close()
        answers[str(i)] = st.text_area(f"Your answer", key=f"mock_answer_{i}", height=100, label_visibility="collapsed")
    st.session_state["mock_interview_answers"] = answers

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True, key="btn_back_mock"):
            goto("interview")
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
        card_open(extra_style="display:flex;justify-content:center;")
        st.markdown(circular_score(evaluation.get("overall_readiness_score", 0), "Interview Readiness"), unsafe_allow_html=True)
        card_close()

        scores = st.columns(3)
        with scores[0]:
            st.metric("Communication", f"{evaluation.get('communication_score', '-')}%")
        with scores[1]:
            st.metric("Technical", f"{evaluation.get('technical_understanding_score', '-')}%")
        with scores[2]:
            st.metric("Confidence", f"{evaluation.get('confidence_score', '-')}%")

        card_open()
        st.markdown("<strong>Feedback</strong>" + "".join(f"<br>- {f}" for f in evaluation.get("feedback", [])), unsafe_allow_html=True)
        card_close()

        if st.button("Career Toolkit", key="btn_mock_to_toolkit"):
            goto("toolkit")


    # Page 6 — Recommended Jobs

# ============================================================================
# Page — Jobs
# ============================================================================
def page_jobs():
    section_heading("Recommended Jobs")
    result = st.session_state["match_result"]
    if result is None:
        st.warning("Run an analysis first.")
        if st.button("Back", key="btn_back_no_jobs"):
            goto("results")
    return

    if st.session_state["recommended_jobs"] is None:
        if st.button("Find Better-Matched Jobs", type="primary", key="btn_find_jobs"):
            try:
                with st.spinner("Finding roles that fit your skills..."):
                    jobs = recommend_jobs(st.session_state["resume_text"], st.session_state["resume_skills"], result["match_score"])
                st.session_state["recommended_jobs"] = jobs
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
        if st.button("Back", key="btn_back_jobs_pre"):
            goto("results")
    return

    for job in st.session_state["recommended_jobs"]:
        render_job_card(job, apply_key="apply_links")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", key="btn_back_jobs_done"):
            goto("results")
    with col2:
        if st.button("Career Toolkit", key="btn_jobs_to_toolkit"):
            goto("toolkit")


    # Page 7 — Career Toolkit

# ============================================================================
# Page — Toolkit
# ============================================================================
def page_toolkit():
    section_heading("Career Toolkit")

    if st.session_state["match_result"] is None:
        st.warning("Run a resume analysis first.")
        if st.button("Back", key="btn_back_no_toolkit"):
            goto("results")
    return

    # Outreach Email
    card_open()
    section_title("Professional Outreach Email")
    if st.button("Generate Email", key="btn_gen_email"):
        try:
            with st.spinner("Drafting..."):
                st.session_state["outreach_email"] = generate_outreach_email(st.session_state["resume_text"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["outreach_email"]:
        st.text_area("Draft", st.session_state["outreach_email"], height=180, key="email_display")
    card_close()

    # Learning Roadmap
    card_open()
    section_title("Learning Roadmap")
    if st.button("Generate Roadmap", key="btn_gen_roadmap"):
        try:
            with st.spinner("Building roadmap..."):
                st.session_state["learning_roadmap"] = generate_learning_roadmap(st.session_state["match_result"]["missing_skills"], st.session_state["jd_text"])
        except RuntimeError as exc:
            st.error(str(exc))
    if st.session_state["learning_roadmap"]:
        st.markdown(st.session_state["learning_roadmap"])
    card_close()

    # Bullet Rewrites
    card_open()
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
    card_close()

    # Download Report
    card_open()
    section_title("Download Report")
    report_md = build_report_markdown(st.session_state)
    st.download_button("Download Career Report (.md)", data=report_md, file_name="careerpilot_report.md", mime="text/markdown", key="btn_download_report")
    card_close()

    if st.button("Back", key="btn_back_toolkit"):
        goto("results")


    # Sidebar Navigation + Router

# ============================================================================
# Sidebar Navigation + Router
# ============================================================================
if st.session_state["page"] != "landing":
    with st.sidebar:
        st.markdown("### CareerPilot AI")
        st.caption("Analyze &bull; Prepare &bull; Apply")
        nav_pages = [
            ("upload_resume", "Upload Resume"),
            ("job_description", "Job Description"),
            ("results", "Results"),
            ("resume_optimize", "Optimize"),
            ("career_readiness", "Career Readiness"),
            ("interview", "Assessment"),
            ("jobs", "Jobs"),
            ("toolkit", "Toolkit"),
        ]
        for page_key, page_label in nav_pages:
            active = "cp-nav-btn-primary" if st.session_state["page"] == page_key else ""
            if st.button(page_label, key=f"nav_{page_key}"):
                goto(page_key)
        divider()
        if st.button("Start Over", key="btn_reset"):
            reset_all()

PAGES = {
    "landing": page_landing,
    "upload_resume": page_upload_resume,
    "job_description": page_job_description,
    "results": page_results,
    "resume_optimize": page_resume_optimize,
    "career_readiness": page_career_readiness,
    "career_readiness_jobs": page_career_readiness_jobs,
    "interview": page_interview,
    "mock_interview": page_mock_interview,
    "jobs": page_jobs,
    "toolkit": page_toolkit,
}

PAGES[st.session_state["page"]]()
