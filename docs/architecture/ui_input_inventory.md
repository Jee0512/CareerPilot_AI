# UI INPUT INVENTORY

This document inventories all user inputs (native Streamlit widgets and custom HTML) across the CareerPilot AI repository, to guide the establishment of the new `.cp-ui` input system.

## Input Inventory Table

| Page | Input | Widget | Purpose | Required? | State Key | Action | Current Styling | New Pattern |
|---|---|---|---|---|---|---|---|---|
| `app.py` | Navigation Menu | `st.navigation` | Main app routing | Yes | N/A | Changes page | Native Streamlit sidebar | Native Streamlit sidebar + tokens |
| `landing.py` | Resume Upload | `st.file_uploader` | Upload resume for instant analysis | Yes | `landing_uploader` | Parses PDF/DOCX, switches page | Native | Native + .cp-ui wrapper |
| `upload_resume.py` | Resume Upload | `st.file_uploader` | Main resume upload | Yes | `resume_uploader_2` | Parses PDF/DOCX | Native inside `st.container` | Native + .cp-card wrapper |
| `upload_resume.py` | Back Button | `st.button` | Navigate back | No | `btn_back_upload` | Switches to landing | Native (Secondary, full width) | Native (Secondary, full width) |
| `upload_resume.py` | Continue Button | `st.button` | Navigate to Job Description | Yes | `btn_continue_upload` | Switches to JD | Native (Primary, full width) | Native (Primary, full width) |
| `job_description.py` | Input Tabs | `st.tabs` | Switch JD input mode | Yes | N/A | Toggles input view | Native | Native |
| `job_description.py` | JD Text (Paste) | `st.text_area` | Paste job description text | No | `jd_text_area_2` | Updates `jd_text` | Native | Native |
| `job_description.py` | JD Upload | `st.file_uploader` | Upload JD file | No | `jd_file_uploader_2` | Updates `jd_text` | Native | Native |
| `job_description.py` | JD URL | `st.text_input` | Enter JD URL | No | `jd_url_input_2` | Reads URL | Native (placeholder) | Native |
| `job_description.py` | Fetch JD Button | `st.button` | Scrape JD URL | No | `btn_fetch_jd_url_2` | Updates `jd_text` | Native (Secondary) | Native (Secondary) |
| `job_description.py` | Analyze Resume Button | `st.button` | Trigger analysis | Yes | `btn_analyze_jd` | Switches to Results | Native (Primary, full width) | Native (Primary, full width) |
| `results.py` | Optimize Resume Button | `st.button` | Route to Optimize | No | `btn_option1` | Switches to Optimize | Native (Primary, full width) | Native (Primary, full width) |
| `results.py` | Find Jobs Button | `st.button` | Route to Jobs | No | `btn_option2` | Switches to Jobs | Native (Secondary, full width) | Native (Secondary, full width) |
| `results.py` | Start Assessment | `st.button` | Route to Interview | No | `btn_direct_assessment` | Switches to Interview | Native (Secondary) | Native (Secondary) |
| `resume_optimize.py` | Generate Optimized | `st.button` | Trigger AI generation | No | `btn_gen_optimized` | AI call, sets state | Native (Primary) | Native (Primary) |
| `resume_optimize.py` | Download PDF | `st.download_button` | Download optimized PDF | No | N/A | Download | Native | Native |
| `resume_optimize.py` | Recalculate Score | `st.button` | Updates Match Score | No | `btn_recalculate` | Computes Match | Native | Native |
| `resume_optimize.py` | Continue Readiness | `st.button` | Route to Readiness | Yes | `btn_optimize_to_readiness` | Switches page | Native (Primary, full width) | Native (Primary, full width) |
| `career_readiness.py` | Generate Plan | `st.button` | Generates 7-day plan | No | `btn_cr_improve` | AI call | Native (Primary, full width) | Native (Primary, full width) |
| `career_readiness.py` | Find Jobs | `st.button` | Route to Jobs | No | `btn_cr_jobs` | Switches page | Native (Secondary, full width) | Native (Secondary, full width) |
| `career_readiness.py` | Unlock Assessment | `st.button` | Route to Interview | No | `btn_unlock_assessment` | Switches page | Native (Primary, full width) | Native (Primary, full width) |
| `interview.py` | Company Name | `st.text_input` | Enter target company | No | `company_name_input` | Sets state | Native | Native |
| `interview.py` | Generate Interview | `st.button` | Trigger AI gen | Yes | `btn_gen_interview` | AI call | Native (Primary) | Native (Primary) |
| `interview.py` | Multiple Choice Q | `st.radio` | Select answer (1-10) | Yes | `_radio_{i}` | Sets answer state | Native | Native |
| `interview.py` | Tech Question Q | `st.text_area` | Type technical answer | Yes | `tech_answer_{i}` | Sets answer state | Native | Native |
| `mock_interview.py` | Answer Text Area | `st.text_area` | Type mock answer | Yes | `mock_answer_{i}` | Sets answer state | Native (collapsed label) | Native |
| `jobs.py` | Find Better Jobs | `st.button` | Recommend jobs | Yes | `btn_find_jobs` | AI call | Native (Primary) | Native (Primary) |
| `toolkit.py` | Generate Email | `st.button` | Gen outreach email | No | `btn_gen_email` | AI call | Native | Native |
| `toolkit.py` | Email Draft | `st.text_area` | View/Edit draft | No | `email_display` | Displays state | Native | Native |
| `toolkit.py` | Download Report | `st.download_button` | Download toolkit report | No | `btn_download_report` | Download | Native | Native |

## Identified States & Patterns
- **Buttons**: Widespread use of `type="primary"` for the main CTA on each page (e.g., "Continue", "Analyze Resume"). Back buttons are typically default (secondary). `use_container_width=True` is common for bottom-navigation layout columns.
- **File Uploader**: Used consistently for resume and JD parsing. Needs a clean idle/drag state styling via CSS if possible, otherwise native.
- **Text Areas/Inputs**: Used for direct text input. Native placeholders and labels are used. 
- **Tabs/Expanders**: Used for grouping complex input options (like the JD modes).
- **Validation/Feedback**: Heavy reliance on `st.spinner()`, `st.success()`, `st.error()`, `st.info()`, `st.warning()`.
- **Sidebar**: The repo uses `st.navigation()` in `app.py` which natively renders Streamlit's sidebar. There are no explicit calls to `st.sidebar` in the application logic.

## Analysis Conclusion
The application heavily relies on native Streamlit widgets for input. Per the instructions, we must NOT recreate these native widgets in HTML. Instead, we should rely on styling them natively via `styles/streamlit.css` where absolutely necessary, but predominantly leave them to Streamlit's internal presentation engine combined with the global theme configuration (`.streamlit/config.toml`). 
For inputs like the File Uploader and Text inputs, we will wrap them in `.cp-card-base` style containers (`.cp-ui` namespaced) to give them proper spatial hierarchy rather than forcing fragile DOM overrides.
