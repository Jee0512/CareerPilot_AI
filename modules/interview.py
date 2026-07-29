"""
interview.py
------------
Module 2 - AI Interview Readiness Test (placement-assessment style).
Generates a category-based test (Aptitude, Verbal, Reasoning, Technical,
Coding) grounded in the resume + job description, then evaluates the
candidate's answers with per-category scoring and explanations.
"""

from modules.gemini_client import generate_json


def generate_interview(resume_text: str, jd_text: str, requires_coding: bool, company_context: str = "") -> dict:
    """Ask Gemini for a structured placement-style test as JSON.

    company_context (optional): scraped text about the target company (About/
    Careers page). When present, this is light RAG — the model is told to
    bias technical/scenario questions toward the company's actual stated
    focus areas or tech stack, not just the generic JD.
    """
    coding_instruction = (
        "Also include exactly ONE coding problem (field 'coding_question') "
        "with a clear problem statement and an example input/output, relevant "
        "to the target role."
        if requires_coding
        else "Set 'coding_question' to null since this role does not require coding."
    )

    company_block = (
        f"""
COMPANY CONTEXT (use this to make technical questions feel specific to this
company's actual focus/tech, where relevant — don't force it if irrelevant):
\"\"\"{company_context[:2500]}\"\"\"
"""
        if company_context
        else ""
    )

    prompt = f"""
You are a senior recruiter building a placement-style screening assessment.

RESUME:
\"\"\"{resume_text[:4000]}\"\"\"

JOB DESCRIPTION:
\"\"\"{jd_text[:4000]}\"\"\"
{company_block}
Build an assessment with these exact sections:
- "aptitude": 5 multiple-choice quantitative/aptitude questions (general, standard placement-test style)
- "verbal": 5 multiple-choice verbal ability questions (grammar, comprehension, vocabulary)
- "reasoning": 5 multiple-choice logical reasoning questions
- "technical": exactly 2 open-ended technical questions that reference the
  candidate's ACTUAL resume skills and the ACTUAL job requirements (not generic)
- "coding_question": see instruction below

Each MCQ item must have: "question", "options" (list of 4, prefixed "A) ".."D) "),
and "answer" (the correct option letter).

{coding_instruction}

Return ONLY valid JSON (no markdown fences, no commentary) with this exact shape:
{{
  "aptitude": [{{"question": "...", "options": ["A) ...","B) ...","C) ...","D) ..."], "answer": "A"}}],
  "verbal": [{{"question": "...", "options": ["...","...","...","..."], "answer": "B"}}],
  "reasoning": [{{"question": "...", "options": ["...","...","...","..."], "answer": "C"}}],
  "technical": ["question 1", "question 2"],
  "coding_question": "problem statement or null"
}}
"""
    return generate_json(prompt, temperature=0.5)


def evaluate_answers(resume_text: str, jd_text: str, interview: dict, answers: dict) -> dict:
    """
    Send the candidate's answers back to Gemini for category-wise scoring.
    `answers` keys mirror the interview structure: aptitude_0..4, verbal_0..4,
    reasoning_0..4, tech_0..1, coding.
    """
    prompt = f"""
You are a senior recruiter scoring a candidate's placement-style assessment.

JOB DESCRIPTION SUMMARY:
\"\"\"{jd_text[:2000]}\"\"\"

TEST QUESTIONS AND THE CANDIDATE'S ANSWERS (JSON):
{{
  "questions": {interview},
  "answers": {answers}
}}

For the MCQ sections (aptitude, verbal, reasoning), score strictly against the
"answer" field already provided in the questions. For technical and coding,
judge correctness, depth, and relevance to the role yourself.

Return ONLY valid JSON (no markdown fences, no commentary) with this exact shape:
{{
  "overall_score": 0-100 integer,
  "category_scores": {{
    "aptitude": 0-100 integer,
    "verbal": 0-100 integer,
    "reasoning": 0-100 integer,
    "technical": 0-100 integer,
    "coding": 0-100 integer or null if no coding question
  }},
  "correct_answers": {{"aptitude": ["A","C","B","D","A"], "verbal": ["..."], "reasoning": ["..."]}},
  "explanations": ["short explanation for each MCQ, in order across aptitude+verbal+reasoning"],
  "strong_areas": ["...", "..."],
  "weak_areas": ["...", "..."],
  "readiness_level": "Not Ready | Needs Practice | Ready | Highly Ready",
  "recommendations": ["specific, actionable tip", "..."]
}}
"""
    return generate_json(prompt, temperature=0.3)


def generate_mock_interview_questions(resume_text: str, jd_text: str) -> list[str]:
    """Generate 3-5 short, spoken-style mock interview questions (e.g. "Tell me about yourself")."""
    prompt = f"""
Generate 3-5 short, common spoken interview questions personalized to this
candidate and role — the kind asked in the first few minutes of a real
interview (e.g. "Tell me about yourself", "Why should we hire you", "Explain
one challenge you faced on [an actual project from their resume]").

RESUME:
\"\"\"{resume_text[:3000]}\"\"\"

JOB DESCRIPTION:
\"\"\"{jd_text[:2000]}\"\"\"

Return ONLY valid JSON (no markdown fences, no commentary) as a list of
plain question strings:
["question 1", "question 2", "question 3"]
"""
    result = generate_json(prompt, temperature=0.5)
    return result if isinstance(result, list) else result.get("questions", [])


def evaluate_mock_interview(resume_text: str, jd_text: str, questions: list[str], answers: list[str]) -> dict:
    """Evaluate short mock-interview answers on communication, technical understanding, and confidence."""
    prompt = f"""
You are an interview coach evaluating a candidate's short spoken-style
interview answers (written form).

JOB DESCRIPTION SUMMARY:
\"\"\"{jd_text[:1500]}\"\"\"

QUESTIONS AND ANSWERS (JSON):
{{"questions": {questions}, "answers": {answers}}}

Evaluate holistically across all answers. Return ONLY valid JSON (no
markdown fences, no commentary) with this exact shape:
{{
  "communication_score": 0-100 integer,
  "technical_understanding_score": 0-100 integer,
  "confidence_score": 0-100 integer,
  "overall_readiness_score": 0-100 integer,
  "feedback": ["specific, constructive tip", "..."]
}}
"""
    return generate_json(prompt, temperature=0.3)
