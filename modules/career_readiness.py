"""
career_readiness.py
--------------------
AI Career Readiness Decision Engine — a new module that sits after Resume
Optimization & Score Recalculation. It provides:
  1. 7-Day Personalized Learning Plan generation
  2. AI Mini Project recommendation
  3. Improvement summary for progress tracking
  4. Skill-based job recommendations (matching current resume, not target JD)

All functions reuse the existing gemini_client.py for AI calls and NEVER
modify any existing backend logic.
"""

from datetime import datetime
from modules.gemini_client import generate_text, generate_json


def generate_7day_learning_plan(resume_text: str, jd_text: str, missing_skills: list[str]) -> str:
    """
    Generate a personalized 7-Day Learning Plan using the uploaded resume,
    job description, and missing skills. Returns formatted markdown text.
    """
    if not missing_skills:
        return "No missing skills detected — you're already well-aligned for this role!"

    prompt = f"""
You are a personalized AI career coach. Create a detailed 7-Day Learning Plan
for a candidate based on their resume, target job description, and identified
skill gaps.

RESUME:
\"\"\"{resume_text[:3000]}\"\"\"

TARGET JOB DESCRIPTION:
\"\"\"{jd_text[:2000]}\"\"\"

SKILLS TO LEARN (missing skills): {missing_skills}

For each day (Day 1 through Day 7), include:
- **Topic**: A specific concept or skill to focus on
- **Concepts**: Key ideas and theory to understand
- **Practice Task**: A hands-on exercise or activity
- **Mini Coding Exercise**: A small coding task if applicable
- **Resources**: Types of resources to use (e.g., official docs, tutorials)
- **Daily Checkpoint**: How to verify learning for the day
- **Expected Outcome**: What the candidate should be able to do by end of day

IMPORTANT: The plan must directly address the missing skills listed above.
Organize learning progressively - fundamentals first, then advanced topics.

Format as plain text with clear "Day 1:", "Day 2:" etc. headings. Keep it
actionable and practical. Under 800 words total.
"""
    return generate_text(prompt, temperature=0.4).strip()


def generate_ai_mini_project(resume_text: str, jd_text: str, missing_skills: list[str]) -> dict:
    """
    Generate exactly ONE beginner-to-intermediate AI mini project that
    directly addresses the candidate's missing skills.
    Returns a structured dict with project details.
    """
    if not missing_skills:
        return {
            "title": "General Portfolio Project",
            "objective": "Build a project that showcases your existing skills",
            "features": ["Apply your current skills to a real-world problem"],
            "technologies": [],
            "skills_learned": [],
            "difficulty": "Beginner",
            "estimated_duration": "1-2 weeks",
            "expected_outcome": "A portfolio-ready project"
        }

    prompt = f"""
You are an AI career mentor. Recommend EXACTLY ONE beginner-to-intermediate
AI mini project that will help a candidate build the missing skills they need
for their target role.

RESUME (candidate's current background):
\"\"\"{resume_text[:2500]}\"\"\"

TARGET JOB DESCRIPTION:
\"\"\"{jd_text[:1500]}\"\"\"

SKILLS TO DEVELOP: {missing_skills}

The project should:
1. Be achievable in 1-2 weeks
2. Directly practice the missing skills listed above
3. Be portfolio-worthy
4. Be beginner-to-intermediate level
5. Build on any related skills the candidate already has

Return ONLY valid JSON (no markdown fences, no commentary) with this exact shape:
{{
  "title": "Project title",
  "objective": "One sentence stating what the project does",
  "features": ["feature 1", "feature 2", "feature 3", "feature 4"],
  "technologies": ["tech1", "tech2", "tech3"],
  "skills_learned": ["skill1", "skill2", "skill3"],
  "difficulty": "Beginner / Intermediate",
  "estimated_duration": "e.g. 1-2 weeks",
  "expected_outcome": "What the candidate will learn and be able to demonstrate"
}}
"""
    result = generate_json(prompt, temperature=0.4)
    # Ensure all required fields exist
    defaults = {
        "title": "AI-Powered Project",
        "objective": "Build a practical AI application",
        "features": ["Core feature implementation"],
        "technologies": ["Python"],
        "skills_learned": missing_skills,
        "difficulty": "Intermediate",
        "estimated_duration": "1-2 weeks",
        "expected_outcome": "Portfolio-ready project demonstrating key skills"
    }
    if isinstance(result, dict):
        for k, v in defaults.items():
            result.setdefault(k, v)
        return result
    return defaults


def generate_improvement_summary(
    previous_score: float,
    new_score: float,
    previous_skills: list[str],
    current_skills: list[str],
    remaining_missing: list[str]
) -> str:
    """
    Generate an AI summary explaining how the resume improved between
    the original and the updated version.
    """
    new_skills = [s for s in current_skills if s not in previous_skills]
    improved = [s for s in previous_skills if s in current_skills]
    improvement = round(new_score - previous_score, 1)

    prompt = f"""
A candidate uploaded an improved resume. Here are the before/after metrics:

Previous Score: {previous_score}%
New Score: {new_score}%
Overall Improvement: {improvement}% ({'+' if improvement >= 0 else ''}{improvement}%)

Previous Skills: {previous_skills}
Current Skills: {current_skills}
New Skills Added: {new_skills}
Improved (retained) Skills: {improved}
Still Missing: {remaining_missing}

Write a brief, encouraging 2-3 sentence summary explaining:
1. How the resume improved
2. What new skills were added or strengthened
3. What still needs work (if anything)

Be specific and constructive. Keep it under 100 words. Do NOT use markdown.
"""
    return generate_text(prompt, temperature=0.3).strip()


def recommend_skill_based_jobs(resume_text: str, resume_skills: list[str]) -> list[dict]:
    """
    Recommend 2-5 jobs that better match the candidate's CURRENT resume/skills
    (rather than the original target role). Includes company names and apply links.
    """
    if not resume_skills:
        return []

    prompt = f"""
A candidate's CURRENT resume has these skills: {resume_skills}

RESUME EXCERPT:
\"\"\"{resume_text[:2500]}\"\"\"

Based SOLELY on their current skills (not a previous target role), suggest
2-5 job titles that would be an excellent match for them RIGHT NOW.

For each job, provide a realistic company name (well-known tech companies),
estimated match percentage (based on skill overlap), matching/missing skills,
and a brief reason why it fits.

Return ONLY valid JSON (no markdown fences, no commentary) as a list:
[
  {{
    "job_title": "e.g. Data Scientist",
    "company": "e.g. Google",
    "estimated_match_pct": 85,
    "reason": "One sentence explaining the fit",
    "skills_present": ["skill from resume", "..."],
    "skills_missing": ["skill to consider learning", "..."],
    "apply_urls": {{
      "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords=Data+Scientist",
      "Indeed": "https://www.indeed.com/jobs?q=Data+Scientist",
      "Naukri": "https://www.naukri.com/data-scientist-jobs",
      "Company Careers": "https://careers.google.com/jobs"
    }}
  }}
]
"""
    from urllib.parse import quote_plus

    result = generate_json(prompt, temperature=0.4)
    jobs = result if isinstance(result, list) else result.get("jobs", result.get("recommendations", []))

    # Ensure apply URLs are present and valid
    for job in jobs:
        if "apply_urls" not in job or not job["apply_urls"]:
            title = job.get("job_title", "")
            q = quote_plus(title)
            job["apply_urls"] = {
                "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={q}",
                "Indeed": f"https://www.indeed.com/jobs?q={q}",
                "Naukri": f"https://www.naukri.com/{q.replace('+', '-')}-jobs",
            }
        if "company" not in job:
            job["company"] = ""

    return jobs[:5]

