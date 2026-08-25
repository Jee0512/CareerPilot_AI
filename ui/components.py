import streamlit as st
from typing import List

# ── Step-track configuration ─────────────────────────────────────────────────
STEP_SEQUENCE = ["upload_resume", "job_description", "results", "resume_optimize"]
STEP_LABELS = {
    "upload_resume": "Upload Resume",
    "job_description": "Job Description",
    "results": "Resume Match Score",
    "resume_optimize": "Optimize & Compare",
}

def render_step_track(current_page: str):
    """Render the multi-step progress tracker using .cp-ui styling."""
    if current_page not in STEP_SEQUENCE:
        return
    
    idx = STEP_SEQUENCE.index(current_page)
    total = len(STEP_SEQUENCE)
    
    bars_html = ""
    for i in range(total):
        bg_color = "var(--cp-color-primary)" if i <= idx else "var(--cp-color-border)"
        bars_html += f'<div style="height: 4px; flex: 1; background: {bg_color}; border-radius: 2px;"></div>'
        
    st.html(f'''
    <div class="cp-ui" style="margin-bottom: var(--cp-space-xl);">
        <div style="font-size: 0.75rem; font-weight: 600; color: var(--cp-color-text-muted); margin-bottom: var(--cp-space-sm); text-transform: uppercase; letter-spacing: 0.05em;">
            Step {idx + 1} of {total} &middot; <span style="color: var(--cp-color-text);">{STEP_LABELS[current_page]}</span>
        </div>
        <div style="display: flex; gap: var(--cp-space-xs); width: 100%;">
            {bars_html}
        </div>
    </div>
    ''')


def render_page_header(title: str, subtitle: str = ""):
    """Render a page section heading with an optional subtitle using .cp-ui typography."""
    subtitle_html = f'<p class="cp-text-body" style="margin-bottom: var(--cp-space-xl);">{subtitle}</p>' if subtitle else ""
    st.html(f'''
    <div class="cp-ui">
        <h1 class="cp-text-h1" style="margin-bottom: var(--cp-space-xs);">{title}</h1>
        {subtitle_html}
    </div>
    ''')


def render_badge_list(items: List[str], variant: str = "good"):
    """Render a list of badge pills using semantic colors."""
    if not items:
        return
        
    color_map = {
        "good": ("var(--cp-color-success)", "var(--cp-color-success-bg)", "rgba(16, 185, 129, 0.2)"),
        "bad": ("var(--cp-color-danger)", "var(--cp-color-danger-bg)", "rgba(239, 68, 68, 0.2)"),
        "warn": ("var(--cp-color-warning)", "var(--cp-color-warning-bg)", "rgba(245, 158, 11, 0.2)"),
        "info": ("var(--cp-color-info)", "var(--cp-color-info-bg)", "rgba(59, 130, 246, 0.2)"),
        "purple": ("var(--cp-color-primary)", "var(--cp-color-surface-inset)", "var(--cp-color-border)")
    }
    
    text_color, bg_color, border_color = color_map.get(variant, color_map["info"])
    
    badges_html = "".join([
        f'<span class="cp-badge-base" style="background: {bg_color}; color: {text_color}; border-color: {border_color}; margin-right: 0.5rem; margin-bottom: 0.5rem;">{item}</span>'
        for item in items
    ])
    
    st.html(f'<div class="cp-ui" style="display: flex; flex-wrap: wrap;">{badges_html}</div>')


def render_circular_score(score: float, label: str = "", size: str = "150px") -> None:
    """Render a circular score gauge using semantic CSS variables."""
    deg = max(0, min(100, score)) * 3.6
    inner_size = f"calc({size} - 24px)"
    font_size = "2rem" if "150" in size else "1.5rem"
    
    if score >= 75:
        ring_color = "var(--cp-color-success)"
    elif score >= 50:
        ring_color = "var(--cp-color-warning)"
    else:
        ring_color = "var(--cp-color-danger)"
        
    st.html(f"""
    <div class="cp-ui" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: var(--cp-space-md) 0;">
      <div style="width:{size}; height:{size}; border-radius:50%;
          background:conic-gradient({ring_color} {deg}deg, var(--cp-color-border) 0deg);
          display:flex; align-items:center; justify-content:center;
          box-shadow:var(--cp-shadow-subtle);">
        <div style="width:{inner_size}; height:{inner_size}; border-radius:50%;
            display:flex; align-items:center; justify-content:center;
            font-size:{font_size}; font-weight:800; background:var(--cp-color-surface); color:var(--cp-color-text);">
          {score}%
        </div>
      </div>
      <div style="margin-top: var(--cp-space-md); font-size: 0.75rem; font-weight: 700; color: var(--cp-color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
    </div>
    """)


def render_section_title(title: str, size: str = "1.25rem") -> None:
    """Render a section title suitable for use within cards."""
    st.html(f'''
    <div class="cp-ui">
        <h3 style="font-size: {size}; font-weight: 700; color: var(--cp-color-text); margin-bottom: var(--cp-space-md);">{title}</h3>
    </div>
    ''')

def render_job_card(job: dict, apply_key: str = "apply_urls"):
    """Render a recommended job card."""
    title = job.get("title") or job.get("job_title", "Role")
    company = job.get("company", "Company")
    match_score = job.get("match_score") or job.get("estimated_match_pct", 0)
    reason = job.get("reason", "")
    
    present = job.get("skills_present", [])
    missing = job.get("skills_missing", [])
    
    present_html = " ".join(f'<span class="cp-badge-base" style="background: var(--cp-color-success-bg); color: var(--cp-color-success); border-color: rgba(16, 185, 129, 0.2); margin-right: 0.5rem; margin-bottom: 0.5rem; font-size: 0.75rem; padding: 0.125rem 0.5rem;">{s}</span>' for s in present) if present else ""
    missing_html = " ".join(f'<span class="cp-badge-base" style="background: var(--cp-color-danger-bg); color: var(--cp-color-danger); border-color: rgba(239, 68, 68, 0.2); margin-right: 0.5rem; margin-bottom: 0.5rem; font-size: 0.75rem; padding: 0.125rem 0.5rem;">{s}</span>' for s in missing) if missing else ""
    
    reason_html = f'<p style="font-size: 0.875rem; color: var(--cp-color-text-secondary); margin-bottom: 16px;">{reason}</p>' if reason else ""
    
    html = f'''
    <div class="cp-ui" style="background: var(--cp-color-surface); border: 1px solid var(--cp-color-border); border-radius: var(--cp-radius-lg); padding: var(--cp-space-xl); margin-bottom: var(--cp-space-lg); display: flex; flex-direction: column; box-shadow: var(--cp-shadow-subtle);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; color: var(--cp-color-text); margin: 0;">{title}</h3>
            <span style="font-weight: 700; color: var(--cp-color-text); background: var(--cp-color-surface-muted); padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; border: 1px solid var(--cp-color-border);">{match_score}% Match</span>
        </div>
        <p style="font-size: 0.875rem; font-weight: 500; color: var(--cp-color-primary); margin-bottom: 16px; margin-top: 0;">{company}</p>
        
        {reason_html}
        
        <p style="font-size: 0.75rem; font-weight: 700; color: var(--cp-color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">Skills</p>
        <div style="display: flex; flex-wrap: wrap;">
            {present_html}
            {missing_html}
        </div>
    </div>
    '''
    st.html(html)
    
    # Handle apply links using native Streamlit buttons
    urls = job.get(apply_key, {})
    if urls and isinstance(urls, dict):
        cols = st.columns(len(urls))
        for col, (site, url) in zip(cols, urls.items()):
            with col:
                st.link_button(f"Apply on {site}", url, use_container_width=True)

