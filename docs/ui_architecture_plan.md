# UI/UX & Architecture Refactoring Plan

## 1. Goal
Modernize the CareerPilot AI application by introducing a cohesive design system, reusable UI components, and a clean routing mechanism that updates the URL without exploding the codebase into dozens of separate physical files (avoiding the rigid Streamlit multipage structure).

## 2. Design System (`assets/style.css`)
We will implement a CSS-variables based design system. This ensures consistency and makes future theming (like dark mode) trivial.

### Core Tokens
- **Primary Colors**: Deep Blue (`#2563EB`) and Indigo (`#4F46E5`) for primary actions.
- **Semantic Colors**:
  - Success: Emerald Green (`#10B981`)
  - Warning: Amber (`#F59E0B`)
  - Error: Rose Red (`#EF4444`)
- **Typography**: Inter (Google Fonts) for clean, modern readability.
- **Glassmorphism**: Subtle translucent backgrounds (`rgba(255, 255, 255, 0.7)`) with backdrop blur for cards and modals.
- **Utility Classes**: Defined in CSS for `cp-card`, `cp-badge`, `cp-metric`, and `cp-animate-in`.

### Integration
- CSS will be injected into Streamlit globally using `st.markdown("<style>...</style>", unsafe_allow_html=True)`.
- Tailwind CSS CDN will be injected to handle structural layout (Flexbox/Grid/Spacing) dynamically.

## 3. Component Refactor (`modules/ui_components.py`)
Currently, HTML strings are repeated throughout the app. We will extract these into a single Python module containing reusable render functions.

### Planned Components
1. **Layout & Typography**
   - `section_heading(title: str)`
   - `section_title(title: str)`
   - `divider()`
2. **Containers**
   - `card_open(extra_classes: str = "")` and `card_close()`
   - `status_banner(message: str, status: str = "info")`
3. **Data Display**
   - `badge_list(items: list, badge_type: str = "primary")`
   - `labeled_badges(label: str, items: list)`
   - `metric_value(label: str, value: str, color_var: str)`
   - `circular_score(score: int, label: str)`
4. **Domain-Specific Cards**
   - `render_job_card(job: dict)`
   - `mentor_card(title: str, text: str)`
   - `decision_card(title: str, action_text: str)`

*Benefit*: This fully removes `unsafe_allow_html=True` spaghetti from the main application files.

## 4. Routing Architecture (The "Not Single URL, Not Multi-Page" Approach)
The user found the 11-file Streamlit native multipage system cumbersome and over-engineered, but dislikes the completely static single-page URL approach.

### The Solution: Query Parameter Routing
Instead of splitting the app into `pages/01_landing.py`, `pages/02_upload.py`, etc., we will keep the modular functions (e.g., `def render_landing():`) inside logical feature modules or a single cleanly organized `app.py`, but we will sync the view state with the browser URL using Streamlit's `st.query_params`.

**How it works:**
1. When navigating, we update both `st.session_state["page"]` AND the browser URL: `st.query_params["view"] = "upload"`.
2. This means the URL will look like `http://localhost:8501/?view=upload`.
3. The user can bookmark specific steps, and the browser's Back/Forward buttons will work.
4. We avoid the rigid Streamlit left-sidebar multipage UI and retain full control over our custom UI and flow.

### Grouped Logical Views
Instead of 11 tiny pages, we can group the flow into major functional views:
- `?view=home` (Landing)
- `?view=analyze` (Upload -> JD -> Results -> Optimize)
- `?view=prepare` (Career Readiness -> Interviews)
- `?view=apply` (Jobs -> Toolkit)

## 5. Execution Steps
1. **Draft CSS Tokens**: Create `assets/style.css` with the design system.
2. **Build Components**: Implement `ui_components.py`.
3. **Refactor App Logic**: Systematically replace all raw HTML in `app.py` with calls to `ui_components`.
4. **Implement Query Routing**: Replace the basic `st.session_state["page"]` routing with `st.query_params` sync to ensure URLs update dynamically without needing separate files.

## Open Questions
- Do you want to keep all the logic inside `app.py` (which keeps it to 1 file), or would you prefer we move the logic for each major view (Analyze, Prepare, Apply) into separate Python modules (e.g., `views/analyze.py`) which are then imported by `app.py`? This keeps the files clean without forcing Streamlit's native multi-page sidebar.
