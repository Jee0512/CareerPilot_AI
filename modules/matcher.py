"""
matcher.py
----------
Compares resume text against a job description using:
  1. Semantic similarity (Sentence-Transformers embeddings + cosine similarity)
  2. Keyword/skill overlap (from resume_parser.extract_skills)
Combines both into ONE final Resume Match Score (no separate ATS/semantic
numbers shown to the user — internally we still blend both signals because
that gives a more reliable score than either alone).
"""

import streamlit as st
from sentence_transformers import SentenceTransformer

from modules.resume_parser import extract_skills


@st.cache_resource(show_spinner=False)
def _load_embedding_model():
    """Small, fast, good-quality embedding model. Cached once per session."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def _semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity between resume and JD embeddings, as a 0-100 score."""
    from sklearn.metrics.pairwise import cosine_similarity
    model = _load_embedding_model()
    embeddings = model.encode([resume_text, jd_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 1)


def _skill_overlap(resume_text: str, jd_text: str) -> dict:
    """Matched/missing skills between resume and job description."""
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    overlap_pct = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0
    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "overlap_pct": round(overlap_pct, 1),
    }


def compute_match(resume_text: str, jd_text: str) -> dict:
    """
    Return a single combined Resume Match Score plus the skill breakdown
    that explains it.

    match_score blends semantic similarity (60%) and skill-keyword overlap
    (40%) - this is what the UI shows as THE score. matched_pct/missing_pct
    are simply match_score and its complement, so the "Matching Skills (X%)"
    / "Missing Skills (Y%)" headers always add up to 100 and stay consistent
    with the headline number.
    """
    sem_score = _semantic_similarity(resume_text, jd_text)
    skills = _skill_overlap(resume_text, jd_text)

    match_score = round(sem_score * 0.6 + skills["overlap_pct"] * 0.4, 1)
    match_score = max(0.0, min(100.0, match_score))

    return {
        "match_score": match_score,
        "matched_pct": match_score,
        "missing_pct": round(100 - match_score, 1),
        "matched_skills": skills["matched"],
        "missing_skills": skills["missing"],
        "extra_skills": skills["extra"],
    }
