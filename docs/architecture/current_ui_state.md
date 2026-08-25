# CURRENT UI STATE REPORT

## Runtime
- **Streamlit version:** >=1.35.0 (per `requirements.txt`)
- **Python version:** 3.12 (per virtual environment execution)
- **Relevant dependencies:** `PyMuPDF`, `sentence-transformers`, `google-genai`, `beautifulsoup4`

## Routing
- **Current router:** `st.navigation`
- **Current pages:** `landing.py`, `upload_resume.py`, `job_description.py`, `results.py`, `resume_optimize.py`, `career_readiness.py`, `career_readiness_jobs.py`, `interview.py`, `mock_interview.py`, `jobs.py`, `toolkit.py`
- **Migration status:** Completed. The legacy `st.session_state["page"]` has been replaced globally for page navigation. `app.py` no longer stores monolithic page view functions.

## State
- **All session-state keys:** Defined in `DEFAULT_STATE` inside `app.py` (`page`, `resume_text`, `resume_skills`, `resume_file_type`, `jd_text`, `match_result`, `interview`, `interview_answers`, `evaluation`, `recommended_jobs`, `outreach_email`, `learning_roadmap`, `bullet_rewrites`, `tailored_resume`, `resume_diff_html`, `section_diffs`, `resume_pdf_bytes`, `resume_layout_lines`, `layout_rewrites`, `optimized_pdf_bytes`, `optimized_resume_text`, `recalculated_match`, `resume_debate`, `mock_interview_questions`, `mock_interview_answers`, `mock_interview_evaluation`, `company_name`, `company_url`, `company_context`, `career_readiness_shown`, `learning_plan_7day`, `ai_mini_project`, `improved_resume_text`, `improved_resume_score`, `improvement_summary`, `career_readiness_jobs`, `progress_history`, `previous_resume_skills`, `career_readiness_origin`)
- **Type/Purpose:** These are primarily primitive values (strings, bytes, dicts, lists) that persist application state between reruns and route transitions. Authoritative application state lives here.
- **Read/write locations:** Initialized in `app.py`, mutated in `pages/*.py` based on business logic events triggered via widgets.

## UI
- **Native widgets:** Extensive usage of `st.button`, `st.file_uploader`, `st.text_area`, `st.text_input`, `st.download_button`, `st.radio`, `st.progress`, `st.spinner`.
- **Custom HTML:** Used for cards, badges, visual score metrics, grids, banners, etc.
- **st.html / unsafe_allow_html:** Almost entirely implemented using `st.markdown(..., unsafe_allow_html=True)`. Very high usage across `modules/ui_components.py` and some page components.

## CSS
- **CSS files:** `assets/style.css`
- **Global CSS:** Loaded explicitly via `st.markdown("<style>...</style>")` in `app.py`. Contains custom classes (`cp-*`) targeting custom HTML.
- **Streamlit overrides:** Very minimal; `[data-testid]` overrides exist occasionally for layout adjustments but the codebase relies primarily on its custom HTML for visual richness.

## Tailwind
- **Tailwind locations:** Previously injected globally.
- **CDN:** `inject_tailwind()` in `modules/ui_components.py` is an empty stub. The CDN is currently inactive because Streamlit strips standard script tags.
- **Classes:** One inert usage of `leading-relaxed mb-6` found in `pages/landing.py`.
- **Files:** The application is entirely independent of Tailwind right now.

## Components
- **Current reusable components:** Defined in `modules/ui_components.py` (e.g. `render_top_navbar`, `render_step_track`, `circular_score`, `section_heading`, `badge_list`, `compare_grid`, `render_job_card`, `success_gradient`).
- **Current UI architecture:** Native Streamlit handles form IO; `ui_components.py` generates HTML strings rendered with `unsafe_allow_html=True` using custom `cp-*` CSS classes.

## Business/UI coupling
- **Major UI Actions:**
  - `upload_resume.py`: Upload button triggers `extract_text_from_pdf`/`docx` and `extract_skills`.
  - `job_description.py`: Analyze button triggers JD validation and `compute_match`.
  - `resume_optimize.py`: Recalculate triggers `generate_tailored_resume` or `generate_layout_constrained_rewrites` and subsequent `compute_match`.
  - `interview.py`: Submission triggers `evaluate_answers`.
  
## Risks
- Reliance on `st.markdown(..., unsafe_allow_html=True)` should ideally be migrated to `st.html()` for safer rendering in future phases.
- Business logic is mostly cleanly separated into `modules/`, but some page logic is dense with nested if/else event handling.
