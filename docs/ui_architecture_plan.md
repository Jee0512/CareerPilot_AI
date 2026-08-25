# CareerPilot AI — Developer Guide
### Architecture, Maintainability & AI Coding Rules

> **Purpose:** This document is the single source of truth for any developer or AI agent working on CareerPilot AI. It describes the physical architecture, current transitional state, UI standards, and strict rules for code maintainability.

---

## 1. Project Folder Structure & Boundaries

The codebase enforces strict boundaries. Do not cross them.

- **`app.py`**: The application entry point. Responsible *only* for session initialization, global CSS loading, shared configuration, and defining `st.navigation`. It **does not** contain UI page functions or business logic.
- **`pages/`**: Contains the physical Streamlit pages (e.g., `landing.py`, `upload_resume.py`, `results.py`). This is the UI layer. Pages orchestrate business logic by calling `modules/`.
- **`modules/`**: Contains all pure business logic and heavy lifting (e.g., `resume_parser.py`, `matcher.py`, `gemini_client.py`). Modules should rarely directly interact with the UI.
- **`styles/`**: The new design foundation (Tokens and CSS).
- **`assets/`**: Legacy CSS and assets (during transition).
- **`ui/`**: Centralized UI primitives, such as `icons.py`.

---

## 2. Application Page Flow & Router

### Current Router
The application uses Streamlit's native multi-page routing architecture:
- `st.navigation()`
- `st.Page()`

**Routing Configuration:**
Routing is defined exclusively in `app.py` via a dictionary of `st.Page` definitions pointing to files in the `pages/` directory.

```python
pages = {
    "CareerPilot": [
        st.Page("pages/landing.py", title="Home", default=True),
        st.Page("pages/upload_resume.py", title="Upload Resume"),
        # ... other pages
    ]
}
pg = st.navigation(pages)
pg.run()
```

### Navigating Programmatically
To navigate between pages programmatically within the app, use the native Streamlit command:
`st.switch_page("pages/target_file.py")`

### Historical / Legacy Routing (DEPRECATED)
*Do not use this architecture.* The old architecture relied on a manual manual router driven by `st.session_state["page"]` and a `goto()` function. This has been entirely removed.

---

## 3. State Management

All authoritative application state lives in `st.session_state`.
The default state is initialized in `app.py` before the router runs.

**Current Core State Keys:**
- `resume_text` (str): Raw extracted resume text.
- `resume_skills` (list): Extracted skills.
- `resume_file_type` (str): 'pdf' or 'docx'.
- `resume_pdf_bytes` (bytes): Raw uploaded file.
- `jd_text` (str): Raw job description.
- `match_result` (dict): Match scores and analysis.
- `interview_answers`, `mock_interview_answers` (dicts): User state.
- `recalculated_match` (dict): Score after optimization.

**Rule:** Do not preserve obsolete state keys (like the old `"page"` router key). If a state variable is no longer needed, remove it.

---

## 4. UI Component Architecture (Transitional)

CareerPilot is currently in an **incremental, page-by-page migration** from a legacy UI system to a new semantic foundation.

### The New UI Foundation (Active for New/Migrated Pages)
- **Reference Page:** `pages/landing.py` is the reference implementation.
- **CSS:** Powered by `styles/tokens.css` (semantic variables) and `styles/base.css` (layout/typography classes).
- **Namespace:** All new custom UI MUST be safely isolated inside a `.cp-ui` DOM namespace.
- **Icons:** Centralized SVG icons live in `ui/icons.py`. Emoji icons are no longer the structural primary icon system.
- **Tailwind:** **NO TAILWIND.** Tailwind CDN is inactive and strictly forbidden. Do not inject or rely on Tailwind utility classes.

### The Legacy UI (Transitional)
- **CSS:** Powered by `assets/style.css`.
- **Components:** Built via `modules/ui_components.py` string templates injected using `st.markdown(..., unsafe_allow_html=True)`.
- **Status:** Coexists globally via `app.py` to keep unmigrated pages (like `results.py` and `upload_resume.py`) working until they are refactored to the new foundation.

### Important Streamlit Widget Rule
- **Use Native Streamlit Components for Interactive Behavior.** If you need a button, use `st.button`. If you need input, use `st.text_input`.
- **Use `st.html()` for Custom Presentational HTML.**
- **NEVER** create fake HTML buttons or inputs when a native Streamlit widget is required for Python interaction. Custom HTML should not bypass Streamlit's interaction model.

---

## 5. CSS Architecture

**CSS Files Loading:**
`app.py` safely loads both the legacy system and the new design tokens simultaneously.

**Rules for New CSS (`styles/base.css` and `styles/streamlit.css`):**
1. **Tokens are Semantic:** Use the `--cp-color-*` and `--cp-space-*` tokens from `tokens.css`.
2. **Custom CSS is Namespaced:** Do not write global selectors like `button {}` or `h1 {}`. All custom styles must be scoped under `.cp-ui`.
3. **No Breakage:** New styling must not break legacy pages.
4. **No Frameworks:** Do not introduce global CSS frameworks (Tailwind, Bootstrap).
5. **Streamlit Saftey:** Do not use arbitrary Streamlit internal DOM selectors (`[data-testid=...]`) unless absolutely necessary, documented, and explicitly scoped.

---

## 6. AI Coding Rules

Future AI coding agents working on this repository **MUST** follow these rules:

1. **Inspect Before Modifying:** Always inspect the repository state before altering architecture. Never assume old documentation reflects the current code.
2. **Read Architecture Documentation:** Consult this guide and `docs/design_system_locked.md` before making UI changes.
3. **Make the Smallest Safe Change:** Do not rewrite the entire app in one go.
4. **No Big-Bang Refactoring:** Never migrate unrelated pages during a scoped task. Use the incremental migration strategy.
5. **Maintain Boundaries:** Never modify business logic (`modules/`) during a UI-only task unless absolutely required to support the UI change.
6. **No Unapproved Frameworks:** Never introduce a framework (React, Vue, Tailwind, FastAPI) without explicit architectural approval from the user.
7. **Validate:** Always validate affected pages after changes. Ensure the app runs and no legacy page was accidentally destroyed.
8. **Update Documentation:** Update this Developer Guide and the Locked Design System when architecture materially changes.
9. **When in doubt, ask:** If there is an unresolved architectural ambiguity, document it and stop for user feedback rather than inventing a solution.

---

> **Note on Historical Stale Instructions:**
> Any references you find in the codebase or git history to `inject_tailwind()`, `PAGES` dictionary routing, `st.query_params["view"]` routing, or dark-mode Apple System Blue are officially deprecated. Do not resurrect them.
