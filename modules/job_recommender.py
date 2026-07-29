"""
job_recommender.py
-------------------
Module 3 — Smart Job Recommendation.
When the resume-to-JD match is weak, ask Gemini to suggest better-fitting
roles based on the candidate's actual skills, then build ready-to-click
search links on major job boards (no paid job-board API required).
"""

from urllib.parse import quote_plus
from modules.gemini_client import generate_json

ELIGIBILITY_THRESHOLD = 75  # Resume-JD match % required to unlock the interview test


def _build_search_links(job_title: str) -> dict:
    q = quote_plus(job_title)
    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={q}",
        "Indeed": f"https://www.indeed.com/jobs?q={q}",
        "Naukri": f"https://www.naukri.com/{q.replace('+', '-')}-jobs",
        "Internshala": f"https://internshala.com/internships/keywords-{q.replace('+', '-')}",
        "Google Jobs": f"https://www.google.com/search?q={q}+jobs&ibp=htl;jobs",
    }


def recommend_jobs(resume_text: str, resume_skills: list[str], ats_score: float) -> list[dict]:
    """
    Return up to 5 recommended jobs, each with title, estimated match %,
    reason, skills present/missing, and apply links.
    """
    prompt = f"""
A candidate's resume scored {ats_score}/100 against a job they applied to
(below {ELIGIBILITY_THRESHOLD} means a poor match). Based on their actual
skills below, suggest 2-3 alternative job titles that would be a much
better fit for them RIGHT NOW.

CANDIDATE SKILLS: {resume_skills}

RESUME EXCERPT:
\"\"\"{resume_text[:2500]}\"\"\"

Return ONLY valid JSON (no markdown fences, no commentary) as a list:
[
  {{
    "job_title": "...",
    "estimated_match_pct": 0-100 integer,
    "reason": "one sentence explaining why this fits the candidate",
    "skills_present": ["...", "..."],
    "skills_missing": ["...", "..."]
  }}
]
"""
    result = generate_json(prompt, temperature=0.4)

    # generate_json returns a dict by default; normalize to a list either way.
    jobs = result if isinstance(result, list) else result.get("jobs", result.get("recommendations", []))

    for job in jobs:
        job["apply_links"] = _build_search_links(job.get("job_title", ""))

    return jobs[:3]
