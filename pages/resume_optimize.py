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


render_step_track("resume_optimize")
section_heading("Optimize & Compare")
result = st.session_state["match_result"]
if result is None:
    st.warning("Run a resume analysis first.")
    if st.button("Back", key="btn_back_no_optimize"):
        st.switch_page("pages/results.py")
st.stop()
is_pdf_origin = st.session_state.get("resume_file_type") == "pdf" and st.session_state["resume_pdf_bytes"]
# Step 1: Generate optimization
if st.session_state["optimized_pdf_bytes"] is None:
    with st.container(border=True):
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
                            st.stop()
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
            st.switch_page("pages/results.py")
st.stop()
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
    with st.container(border=True):
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
# Step 3: PDF Preview
divider()
section_title("PDF Preview")
b64_pdf = base64.b64encode(st.session_state["optimized_pdf_bytes"]).decode()
st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" style="border-radius:12px;border:1px solid #E5E7EB;"></iframe>', unsafe_allow_html=True)
# Step 4: Download options (AFTER comparison)
divider()
with st.container(border=True):
    section_title("Download Optimized Resume", size="1.25rem")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button("Download as PDF (design preserved)", data=st.session_state["optimized_pdf_bytes"],
            file_name="optimized_resume.pdf", mime="application/pdf", key="btn_download_pdf",)
    with dcol2:
        st.download_button("Download as DOCX (text only)", data=build_resume_docx(st.session_state["optimized_resume_text"]),
            file_name="optimized_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_download_docx",)
    st.caption("The PDF preserves your exact original design. The DOCX is a clean text re-export.")
# Step 5: Recalculate score - IMPROVED with score comparison
with st.container(border=True):
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
            labeled_badges("Γ£à Matched Skills:", recalc["matched_skills"], "good")
        if recalc["missing_skills"]:
            st.markdown("<br>", unsafe_allow_html=True)
            labeled_badges("Γ¥î Still Missing:", recalc["missing_skills"], "bad")
    if recalc["match_score"] >= ELIGIBILITY_THRESHOLD:
        status_banner("≡ƒÄë Your optimized resume now meets the assessment threshold!", "good")
    else:
        status_banner("Your resume has improved! Additional preparation is recommended before the assessment.", "warn")
card_close()
col1, col2 = st.columns(2)
with col1:
    if st.button("Back", use_container_width=True, key="btn_back_optimize"):
        st.switch_page("pages/results.py")
with col2:
    if st.session_state["recalculated_match"]:
        if st.button("Continue to Career Readiness", use_container_width=True, type="primary", key="btn_optimize_to_readiness"):
            st.session_state["career_readiness_shown"] = False
            st.switch_page("pages/career_readiness.py")
    else:
        st.button("Continue", use_container_width=True, type="primary", disabled=True, key="btn_optimize_disabled")
# Page 4c ΓÇö AI Career Readiness Decision Engine


