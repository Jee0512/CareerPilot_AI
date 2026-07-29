"""
jd_input.py
-----------
Module for Page 3's three job-description input modes:
  1. Manual paste (handled directly in app.py, no helper needed)
  2. LinkedIn job URL -> best-effort scrape of the visible description
  3. Job title -> Gemini generates a realistic representative JD

LinkedIn actively blocks most scraping and often requires login, so the URL
path is best-effort with a clear fallback: if scraping fails, we tell the
user and let them fall back to pasting manually or searching by title.
"""

import requests
from bs4 import BeautifulSoup

from modules.gemini_client import generate_text

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def extract_jd_from_url(url: str) -> str:
    """
    Best-effort fetch of a job posting's visible text from a URL (LinkedIn
    or otherwise). Returns the extracted text, or raises RuntimeError with a
    user-friendly message if the page can't be read (common for LinkedIn,
    which requires login for most postings).
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Couldn't reach that URL. It may require login or be blocking automated access."
        ) from exc

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try common containers first (LinkedIn's public posting pages use this class;
    # other job boards vary, so we fall back to the whole page's text).
    candidates = soup.find_all(["section", "div"], class_=lambda c: c and "description" in c.lower())
    text = ""
    for tag in candidates:
        chunk = tag.get_text(separator="\n", strip=True)
        if len(chunk) > len(text):
            text = chunk

    if not text:
        text = soup.get_text(separator="\n", strip=True)

    text = "\n".join(line for line in text.splitlines() if line.strip())

    if len(text) < 200:
        raise RuntimeError(
            "This page didn't return enough readable content (likely needs login). "
            "Try pasting the job description manually instead, or search by job title."
        )
    return text[:6000]


def generate_sample_jd(job_title: str) -> str:
    """Ask Gemini for a realistic, representative JD for a given job title."""
    prompt = f"""
Write a realistic, representative job description for the role: "{job_title}".

Include: a short intro, a "Responsibilities" section (5-7 bullet points),
and a "Requirements" section (5-7 bullet points covering typical skills,
tools, and experience for this role). Keep it plain text, no markdown
headers with #, just clear section labels and bullet points using "-".
Keep the whole thing under 350 words.
"""
    return generate_text(prompt, temperature=0.4).strip()


def fetch_company_context(url: str) -> str:
    """
    Best-effort fetch of a company's public page (About/Careers/homepage)
    for light RAG context — pulled into the interview prompt so questions
    can reference the company's actual stated focus/tech, not just the JD.
    Raises RuntimeError with a friendly message if the page can't be read.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Couldn't reach that company page. Skipping company context — "
            "the interview will still generate from your resume and the JD."
        ) from exc

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.splitlines() if line.strip())

    if len(text) < 100:
        raise RuntimeError("This page didn't return enough readable content.")
    return text[:3000]
