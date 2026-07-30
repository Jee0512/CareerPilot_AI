"""
ui_components.py
-----------------
Reusable UI rendering helpers for the CareerPilot AI Streamlit app.

Provides component functions that generate clean HTML using CSS classes
from assets/style.css, eliminating inline styles from app.py.
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

# ── Tailwind CDN (Play CDN for Streamlit — no build step needed) ─────────────
TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'


# ═══════════════════════════════════════════════════════════════════════════════
# Layout Components
# ═══════════════════════════════════════════════════════════════════════════════

def inject_tailwind():
    """Inject Tailwind CSS v3 Play CDN into the Streamlit page."""
    st.markdown(TAILWIND_CDN, unsafe_allow_html=True)


def render_top_navbar():
    """Render the premium top navigation bar."""
    st.markdown("""
    <nav class="cp-navbar">
        <a class="cp-nav-logo" href="#">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="#2563EB"/>
                <circle cx="16" cy="16" r="8" fill="white" opacity="0.9"/>
                <path d="M16 10 L20 16 L16 22 L12 16 Z" fill="#2563EB"/>
            </svg>
            Career<span>Pilot</span>
        </a>
        <div class="cp-nav-links">
            <a href="#" onclick="return false;">Home</a>
            <a href="#" onclick="return false;">Features</a>
            <a href="#" onclick="return false;">Dashboard</a>
            <a href="#" onclick="return false;">Roadmap</a>
            <a href="#" onclick="return false;">Interview</a>
        </div>
        <div class="cp-nav-actions">
            <button class="cp-nav-btn">Login</button>
            <button class="cp-nav-btn cp-nav-btn-primary">Get Started</button>
        </div>
    </nav>
    """, unsafe_allow_html=True)


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
    st.markdown(f'<h2 class="mb-2">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<p class="text-gray-500 mb-6">{subtitle}</p>',
            unsafe_allow_html=True,
        )


def section_title(title: str, icon: str = "", size: str = "1rem"):
    """Render a smaller section title (h3) inside cards."""
    prefix = f"{icon} " if icon else ""
    st.markdown(
        f'<h3 class="mb-3" style="font-size:{size};">{prefix}{title}</h3>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Card Wrappers
# ═══════════════════════════════════════════════════════════════════════════════

def card_open(extra_classes: str = "", extra_style: str = ""):
    """Open a card wrapper div. Must be paired with card_close()."""
    style_attr = f' style="{extra_style}"' if extra_style else ""
    st.markdown(
        f'<div class="cp-card {extra_classes}"{style_attr}>',
        unsafe_allow_html=True,
    )


def card_close():
    """Close a card wrapper div."""
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Status & Feedback
# ═══════════════════════════════════════════════════════════════════════════════

def status_banner(text: str, variant: str = "good"):
    """Render a colored status banner. variant: 'good', 'bad', or 'warn'."""
    st.markdown(f'<div class="cp-status-{variant}">{text}</div>', unsafe_allow_html=True)


def privacy_note(text: str = "&#128274; Your data is private and never stored permanently."):
    """Render a small centered privacy notice."""
    st.markdown(
        f'<p class="text-center text-xs text-gray-400">{text}</p>',
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
    """Render a label followed by badges, e.g. '✅ Matched Skills: [Python] [SQL]'."""
    if not items:
        return
    badges = " ".join(f'<span class="cp-badge cp-badge-{variant}">{item}</span>' for item in items)
    st.markdown(f"**{label}** {badges}", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Score Components
# ═══════════════════════════════════════════════════════════════════════════════

def circular_score(score: float, label: str = "", size: str = "150px") -> str:
    """Return HTML for a circular score gauge. green >80, orange 60-80, red <60."""
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
          transition:all 0.5s ease;">
        <div style="width:{inner_size};height:{inner_size};border-radius:50%;background:#fff;
            display:flex;align-items:center;justify-content:center;
            font-size:{font_size};font-weight:800;color:var(--cp-text);">
          {score}%
        </div>
      </div>
      <div class="cp-score-label">{label}</div>
    </div>
    """


def metric_value(label: str, value: str, color: str = ""):
    """Render a single metric (label + big number)."""
    color_style = f' style="color:{color};"' if color else ""
    st.markdown(
        f'<div class="cp-metric">'
        f'<div class="cp-metric-label">{label}</div>'
        f'<div class="cp-metric-value"{color_style}>{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Job Card (DRY — used in 3 pages)
# ═══════════════════════════════════════════════════════════════════════════════

def render_job_card(job: dict, apply_key: str = "apply_links"):
    """Render a single job recommendation card. Eliminates the 3x duplication."""
    card_open()
    title = job.get("job_title", "Role")
    company = job.get("company", "")
    title_display = f"{title} at {company}" if company else title
    section_title(title_display, size="1.1rem")
    st.markdown(f"**Estimated Match:** {job.get('estimated_match_pct', '-')}%")
    st.progress(min(1.0, (job.get("estimated_match_pct") or 0) / 100))
    st.caption(job.get("reason", ""))
    badge_list(job.get("skills_present", []), "good")
    badge_list(job.get("skills_missing", []), "bad")
    urls = job.get(apply_key, job.get("apply_urls", {}))
    for site in ("LinkedIn", "Indeed", "Naukri", "Company Careers"):
        if site in urls:
            st.link_button(f"Apply on {site}", urls[site], use_container_width=True)
    card_close()


# ═══════════════════════════════════════════════════════════════════════════════
# Comparison / Diff Components
# ═══════════════════════════════════════════════════════════════════════════════

def compare_grid(original_html: str, optimized_html: str,
                 original_label: str = "Original &#10060;",
                 optimized_label: str = "Optimized &#9989;"):
    """Render a two-panel before/after comparison grid."""
    st.markdown(f"""
    <div class="cp-compare-grid">
        <div class="cp-compare-original">
            <div class="cp-compare-label">{original_label}</div>
            <div class="text-sm leading-relaxed">{original_html}</div>
        </div>
        <div class="cp-compare-optimized">
            <div class="cp-compare-label">{optimized_label}</div>
            <div class="text-sm leading-relaxed">{optimized_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def score_comparison(prev_score: float, new_score: float):
    """Render a 3-column score comparison (Previous → New → Improvement)."""
    improvement = round(new_score - prev_score, 1)
    sign = "+" if improvement >= 0 else ""
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        metric_value("Previous Score", f"{prev_score}%", "var(--cp-danger)")
    with sc2:
        metric_value("Optimized Score", f"{new_score}%", "var(--cp-success)")
    with sc3:
        color = "var(--cp-success)" if improvement >= 0 else "var(--cp-danger)"
        metric_value("Improvement", f"{sign}{improvement}%", color)


# ═══════════════════════════════════════════════════════════════════════════════
# Decision Cards (Career Readiness)
# ═══════════════════════════════════════════════════════════════════════════════

def decision_card(icon: str, title: str, description: str, bg_color: str = "#EEF4FF",
                  animation: str = "cp-animate-in"):
    """Render a decision card with icon circle, title, and description."""
    st.markdown(f"""
    <div class="cp-decision-card {animation}">
        <div class="cp-icon-circle" style="background:{bg_color};">
            {icon}
        </div>
        <h3 style="font-size:1.1rem;margin-bottom:0.5rem;">{title}</h3>
        <p class="text-gray-500 text-sm mb-5">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def success_gradient(emoji: str, title: str, message: str):
    """Render a green success gradient card."""
    st.markdown(f"""
    <div class="cp-success-gradient cp-animate-in">
        <div class="text-5xl mb-3">{emoji}</div>
        <h3 class="mb-2" style="color:var(--cp-success-text);">{title}</h3>
        <p style="color:#047857;font-size:1rem;max-width:600px;margin:0 auto;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


def mentor_card(emoji: str, title: str, message: str):
    """Render a blue mentor guidance card."""
    st.markdown(f"""
    <div class="cp-mentor-card cp-animate-in">
        <div class="text-5xl mb-3">{emoji}</div>
        <h3 class="mb-2" style="color:var(--cp-info-text);">{title}</h3>
        <p style="color:#3B82F6;font-size:0.95rem;max-width:650px;margin:0 auto;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


def divider():
    """Render a horizontal rule divider."""
    st.markdown("<hr>", unsafe_allow_html=True)
