"""
ui_components.py
-----------------
Reusable UI rendering helpers for the CareerPilot AI Streamlit app.

Provides component functions that generate clean HTML using CSS classes
mapped directly to our `--cp-*` design tokens from assets/style.css.
"""

import streamlit as st
from typing import Optional


# ── Step-track configuration ─────────────────────────────────────────────────
STEP_SEQUENCE = ["upload_resume", "job_description", "results", "resume_optimize"]
STEP_LABELS = {
    "upload_resume": "Upload Resume",
    "job_description": "Job Description",
    "results": "Resume Match Score",
    "resume_optimize": "Optimize & Compare",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Layout Components
# ═══════════════════════════════════════════════════════════════════════════════

def inject_tailwind():
    """No longer injecting Tailwind CDN due to Streamlit stripping script tags. 
    Using native CSS structural classes."""
    pass


def render_top_navbar():
    """Render the premium top navigation bar with bulletproof flex CSS."""
    st.markdown('''
    <div class="cp-navbar">
        <a class="cp-nav-logo" href="#">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="var(--cp-primary)"/>
                <circle cx="16" cy="16" r="8" fill="white" opacity="0.9"/>
                <path d="M16 10 L20 16 L16 22 L12 16 Z" fill="var(--cp-primary)"/>
            </svg>
            Career<span>Pilot</span>
        </a>
        <div class="cp-nav-links">
            <a href="#" onclick="return false;">Home</a>
            <a href="#" onclick="return false;">Features</a>
            <a href="#" onclick="return false;">Dashboard</a>
            <a href="#" onclick="return false;">Interview</a>
        </div>
        <div class="cp-nav-actions">
            <button class="cp-nav-btn">Login</button>
            <button class="cp-nav-btn cp-nav-btn-primary">Get Started</button>
        </div>
    </div>
    <hr style="margin-top:16px; margin-bottom:32px; border:none; border-top:1px solid var(--cp-border);">
    ''', unsafe_allow_html=True)


def render_step_track(current_page: str):
    """Render the multi-step progress tracker."""
    if current_page not in STEP_SEQUENCE:
        return
    idx = STEP_SEQUENCE.index(current_page)
    bars = "".join(
        f'<div class="cp-step {"cp-step-done" if i <= idx else ""}"></div>'
        for i in range(len(STEP_SEQUENCE))
    )
    st.markdown(
        f'<div class="cp-step-label">Step {idx + 1} of {len(STEP_SEQUENCE)} &middot; {STEP_LABELS[current_page]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="cp-step-track">{bars}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Typography Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def section_heading(title: str, subtitle: str = ""):
    """Render a page section heading with an optional subtitle."""
    st.markdown(f'<h2 class="cp-mb-4">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<p class="cp-mb-4" style="color:var(--cp-text-secondary);">{subtitle}</p>',
            unsafe_allow_html=True,
        )


def section_title(title: str, icon: str = "", size: str = "1.25rem"):
    """Render a smaller section title (h3) inside cards."""
    prefix = f"{icon} " if icon else ""
    st.markdown(
        f'<h3 class="cp-mb-4" style="font-size:{size};">{prefix}{title}</h3>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Card Wrappers
# ═══════════════════════════════════════════════════════════════════════════════

def card_open(extra_classes: str = "", extra_style: str = ""):
    """Opens a .cp-card div. Must be paired with card_close()."""
    st.markdown(f'<div class="cp-card {extra_classes}" style="{extra_style}">', unsafe_allow_html=True)

def card_close():
    """Closes a .cp-card div."""
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Status & Feedback
# ═══════════════════════════════════════════════════════════════════════════════

def status_banner(text: str, variant: str = "good"):
    """Render a colored status banner. variant: 'good', 'bad', 'warn', 'info'."""
    st.markdown(f'<div class="cp-status-{variant}">{text}</div>', unsafe_allow_html=True)


def privacy_note(text: str = "&#128274; Your data is private and never stored permanently."):
    """Render a small centered privacy notice."""
    st.markdown(
        f'<p style="text-align:center; font-size:0.8125rem; color:var(--cp-text-muted); margin-top:8px;">{text}</p>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Badge Lists
# ═══════════════════════════════════════════════════════════════════════════════

def badge_list(items: list, variant: str = "good"):
    """Render a list of badge pills. variant: 'good', 'bad', 'warn', 'info', 'purple'."""
    if not items:
        return
    html = " ".join(f'<span class="cp-badge cp-badge-{variant}">{item}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)


def labeled_badges(label: str, items: list, variant: str = "good"):
    """Render a label followed by badges."""
    if not items:
        return
    badges = " ".join(f'<span class="cp-badge cp-badge-{variant}">{item}</span>' for item in items)
    st.markdown(f"<strong style='color:var(--cp-text); margin-right:8px;'>{label}</strong> {badges}", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Score Components
# ═══════════════════════════════════════════════════════════════════════════════

def circular_score(score: float, label: str = "", size: str = "150px") -> str:
    """Return HTML for a circular score gauge."""
    deg = max(0, min(100, score)) * 3.6
    inner_size = f"calc({size} - 32px)"
    font_size = "2rem" if "150" in size else "1.5rem"
    
    if score >= 80:
        ring_color = "var(--cp-success)"
    elif score >= 60:
        ring_color = "var(--cp-warning)"
    else:
        ring_color = "var(--cp-danger)"
        
    return f"""
    <div class="cp-circular-wrapper">
      <div style="width:{size};height:{size};border-radius:50%;
          background:conic-gradient({ring_color} {deg}deg, var(--cp-border) 0deg);
          display:flex;align-items:center;justify-content:center;
          transition:all 0.5s ease; box-shadow:var(--cp-shadow-xs);">
        <div style="width:{inner_size};height:{inner_size};border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:{font_size};font-weight:800; background:var(--cp-bg-card); color:var(--cp-text);">
          {score}%
        </div>
      </div>
      <div style="margin-top:16px; font-size:0.8125rem; font-weight:700; color:var(--cp-text-secondary); text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
    </div>
    """


def metric_value(label: str, value: str, color: str = ""):
    """Render a single metric (label + big number)."""
    color_style = f'color:var(--cp-{color});' if color else 'color:var(--cp-text);'
    st.markdown(
        f'<div class="cp-metric">'
        f'<div class="cp-metric-value" style="{color_style}">{value}</div>'
        f'<div class="cp-metric-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Domain-Specific Cards
# ═══════════════════════════════════════════════════════════════════════════════

def score_comparison(prev_score: float, new_score: float):
    """Render a 3-column layout comparing previous score and new score."""
    diff = new_score - prev_score
    diff_sign = "+" if diff > 0 else ""
    diff_color = "success" if diff > 0 else "danger" if diff < 0 else "text-secondary"
    
    html = f'''
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; text-align:center; padding:24px; background:var(--cp-bg); border:1px solid var(--cp-border); border-radius:var(--cp-radius-md); margin-bottom:24px;">
        <div>
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Original Score</div>
            <div style="font-size:1.5rem; font-weight:800; color:var(--cp-text);">{prev_score:.0f}%</div>
        </div>
        <div style="border-left:1px solid var(--cp-border); border-right:1px solid var(--cp-border);">
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Optimized Score</div>
            <div style="font-size:1.5rem; font-weight:800; color:var(--cp-primary);">{new_score:.0f}%</div>
        </div>
        <div>
            <div style="font-size:0.75rem; font-weight:700; color:var(--cp-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Improvement</div>
            <div style="font-size:1.5rem; font-weight:800; color:var(--cp-{diff_color});">{diff_sign}{diff:.0f}%</div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_job_card(job: dict, apply_key: str = "apply_links"):
    """Render a recommended job card using a single HTML string."""
    present = job.get("skills_present", [])
    missing = job.get("skills_missing", [])
    
    present_html = " ".join(f'<span class="cp-badge cp-badge-good">{s}</span>' for s in present) if present else ""
    missing_html = " ".join(f'<span class="cp-badge cp-badge-bad">{s}</span>' for s in missing) if missing else ""
    
    html = f'''
    <div class="cp-card">
        <h3 style="font-size:1.125rem; margin-bottom:4px;">{job.get("title", "Job Title")}</h3>
        <p class="cp-text-primary" style="font-size:0.875rem; font-weight:500; margin-bottom:16px;">{job.get("company", "Company")}</p>
        <p style="font-size:0.75rem; font-weight:700; color:var(--cp-text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">Required Skills</p>
        {present_html}
        {missing_html}
        <div style="flex-grow:1;"></div>
        <div class="cp-flex-between cp-mt-4" style="border-top:1px solid var(--cp-border); padding-top:16px;">
            <span style="font-size:0.8125rem; font-weight:500; color:var(--cp-text-muted);">Match Score:</span>
            <span style="font-weight:700; color:var(--cp-text);">{job.get("match_score", 0)}%</span>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def compare_grid(left_html: str, right_html: str):
    """Render a two-column CSS grid for comparisons."""
    html = f'''
    <div class="cp-compare-grid">
        <div class="cp-compare-original">
            <div class="cp-compare-label">Original Content (Red = Removed)</div>
            <div style="font-size:0.875rem;line-height:1.6;">{left_html}</div>
        </div>
        <div class="cp-compare-optimized">
            <div class="cp-compare-label">Optimized Content (Green = Added)</div>
            <div style="font-size:0.875rem;line-height:1.6;">{right_html}</div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def decision_card(icon: str, title: str, description: str, bg_color: str, animation: str):
    """Render a card for career decisions."""
    # bg_color is ignored in favor of design system
    st.markdown(
        f'<div class="cp-decision-card {animation}">'
        f'<div class="cp-icon-circle" style="background:var(--cp-primary-light); color:var(--cp-primary);">{icon}</div>'
        f'<h3 style="font-size:1.125rem; margin-bottom:8px;">{title}</h3>'
        f'<p style="font-size:0.875rem; color:var(--cp-text-secondary);">{description}</p>'
        f'</div>',
        unsafe_allow_html=True
    )


def success_gradient(emoji: str, title: str, message: str):
    """Render text with a success gradient."""
    st.markdown(
        f'<div class="cp-success-gradient">'
        f'<div style="font-size:2.5rem; margin-bottom:12px;">{emoji}</div>'
        f'<h2 style="color:#065F46; margin-bottom:8px;">{title}</h2>'
        f'<p style="color:#047857; font-weight:500;">{message}</p>'
        f'</div>', 
        unsafe_allow_html=True
    )


def mentor_card(emoji: str, title: str, message: str):
    """Render an AI Mentor tip card."""
    st.markdown(
        f'<div class="cp-mentor-card">'
        f'<div style="font-size:2.5rem; margin-bottom:12px;">{emoji}</div>'
        f'<h2 style="color:#1E3A8A; margin-bottom:8px;">{title}</h2>'
        f'<p style="color:#1E40AF; font-weight:500;">{message}</p>'
        f'</div>', 
        unsafe_allow_html=True
    )


def divider():
    """Render a standard divider line."""
    st.markdown('<hr>', unsafe_allow_html=True)
