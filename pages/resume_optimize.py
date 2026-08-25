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
    render_section_title, render_badge_list
)

def render_local_score_comparison(prev_score: float, new_score: float):
    diff = new_score - prev_score
    diff_sign = "+" if diff > 0 else ""
    diff_color = "var(--cp-color-success)" if diff > 0 else "var(--cp-color-danger)" if diff < 0 else "var(--cp-color-text-secondary)"
    
    html = f'''
    <div class="cp-ui" style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:var(--cp-space-md); text-align:center; padding:var(--cp-space-lg); background:var(--cp-color-surface); border:1px solid var(--cp-color-border); border-radius:var(--cp-radius-lg); margin-bottom:var(--cp-space-lg);">
        <div>
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-color-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Original Score</div>
            <div style="font-size:2rem; font-weight:800; color:var(--cp-color-text);">{prev_score:.0f}%</div>
        </div>
        <div style="border-left:1px solid var(--cp-color-border); border-right:1px solid var(--cp-color-border);">
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-color-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Optimized Score</div>
            <div style="font-size:2rem; font-weight:800; color:var(--cp-color-primary);">{new_score:.0f}%</div>
        </div>
        <div>
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-color-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Improvement</div>
            <div style="font-size:2rem; font-weight:800; color:{diff_color};">{diff_sign}{diff:.0f}%</div>
        </div>
    </div>
    '''
    st.html(html)

render_step_track("resume_optimize")
render_page_header("Optimize & Compare")
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
render_section_title("Before vs After Comparison")
st.markdown("Review the changes the AI made to your resume, section by section.")

# Two-panel diff view
section_diffs = st.session_state.get("section_diffs")
if section_diffs:
    for sec in section_diffs:
        render_section_title(f"{sec['name']}")
        if sec["changed"] and sec["diff_html"]:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Original Content** (Red = Removed)")
                st.html(f"<div class='cp-ui' style='font-size:0.875rem;line-height:1.6;'>{sec['diff_html']}</div>")
            with cols[1]:
                st.markdown("**Optimized Content** (Green = Added)")
                st.html(f"<div class='cp-ui' style='font-size:0.875rem;line-height:1.6;'>{sec['diff_html']}</div>")
        else:
            st.caption("No changes in this section.")
else:
    # Fallback: show the full diff
    with st.container(border=True):
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Original Content** (Red = Removed)")
            st.html(f"<div class='cp-ui' style='font-size:0.85rem;line-height:1.5;'>{st.session_state['resume_diff_html']}</div>")
        with cols[1]:
            st.markdown("**Optimized Content** (Green = Added)")
            st.html(f"<div class='cp-ui' style='font-size:0.85rem;line-height:1.5;'>{st.session_state['resume_diff_html']}</div>")
            
# Step 3: PDF Preview
st.divider()
render_section_title("PDF Preview")
b64_pdf = base64.b64encode(st.session_state["optimized_pdf_bytes"]).decode()
st.markdown(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="500" style="border-radius:12px;border:1px solid #E5E7EB;"></iframe>', unsafe_allow_html=True)
# Step 4: Download options (AFTER comparison)
st.divider()
with st.container(border=True):
    render_section_title("Download Optimized Resume")
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
    render_section_title("Recalculate Match Score")
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
        render_local_score_comparison(orig_score, recalc['match_score'])
        if recalc["matched_skills"]:
            st.markdown("**✅ Matched Skills:**")
            st.info(", ".join(recalc["matched_skills"]))
        if recalc["missing_skills"]:
            st.markdown("**❌ Still Missing:**")
            st.warning(", ".join(recalc["missing_skills"]))
    
    if st.session_state.get("recalculated_match"):
        if st.session_state["recalculated_match"]["match_score"] >= ELIGIBILITY_THRESHOLD:
            st.success("🎉 Your optimized resume now meets the assessment threshold!")
        else:
            st.warning("Your resume has improved! Additional preparation is recommended.")

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


