# CareerPilot AI 🧭

**Analyze • Prepare • Apply**

An AI career assistant that answers three questions for any job seeker:
1. Am I suitable for this job?
2. Can I clear the interview?
3. If not, what should I apply for instead?

## Features

- **Resume Analysis** — PDF parsing (PyMuPDF) + semantic similarity (Sentence-Transformers)
  and skill-keyword matching → a single **Resume Match Score**, with a matching-skills /
  missing-skills breakdown that always adds up to that score.
- **Flexible Job Description input** — paste manually, fetch from a job URL
  (best-effort scrape), or just search by job title and let Gemini generate a
  representative JD.
- **AI Interview Readiness Test** — unlocked at a 75%+ Resume Match Score.
  A placement-style assessment (5 Aptitude, 5 Verbal, 5 Reasoning MCQs, 2
  Technical questions, +1 coding question when relevant), scored per category
  with explanations, strong/weak areas, and a readiness level.
- **Smart Job Recommendation** — below 75%, Gemini suggests better-fitting
  roles with match %, reasoning, skill gaps, and Apply-on-LinkedIn/Indeed links.
- **Career Toolkit** — a tailored outreach email draft, a personalized
  learning roadmap for missing skills, and a downloadable Markdown report
  bundling the whole session.

## Project Structure

```
careerpilot_ai/
├── app.py                        # Streamlit entry point, 7-page router
├── .streamlit/config.toml        # Light blue/purple theme
├── modules/
│   ├── gemini_client.py          # Gemini API wrapper (key loading, JSON parsing, errors)
│   ├── resume_parser.py          # PDF text extraction + skill extraction
│   ├── matcher.py                # Embeddings, cosine similarity, single Resume Match Score
│   ├── jd_input.py                # Manual / URL-fetch / title-generated JD input
│   ├── interview.py              # Placement-style interview generation + evaluation
│   ├── job_recommender.py        # Alternate job suggestions + search links
│   └── career_tools.py           # Outreach email, learning roadmap, report builder
├── sample_data/
│   ├── sample_resume.pdf         # Try the app with this
│   └── sample_job_description.txt
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup (VS Code / local)

1. **Clone/open the folder in VS Code.**

2. **Create a virtual environment** (Terminal in VS Code):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
   (This now also installs `requests` and `beautifulsoup4`, used for the
   job-URL fetch mode on the Job Description page.)

4. **Get a free Gemini API key:** https://aistudio.google.com/apikey

5. **Set up your API key locally:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and paste your key:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

6. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   It opens at `http://localhost:8501`.

7. **Try it** with `sample_data/sample_resume.pdf` and
   `sample_data/sample_job_description.txt` (paste its contents into the JD box).

### Recommended VS Code extensions
- Python (Microsoft)
- Pylance
- Even Better TOML (for `.streamlit/secrets.toml` if you use it)

## Deployment (Hugging Face Spaces)

1. Create a new Space → SDK: **Streamlit**.
2. Push this folder's contents to the Space repo (everything except `.env`,
   which is gitignored — never commit real API keys).
3. In the Space settings, add a **Secret** named `GEMINI_API_KEY` with your key.
   The app reads it automatically via `st.secrets` — no code changes needed.
4. The Space builds `requirements.txt` automatically and runs `app.py`.

> Note: `en_core_web_sm` needs to be downloaded at build time. Add a
> `packages.txt`/build step or switch `resume_parser.py`'s fallback
> (`spacy.blank("en")`) if you want a zero-download deploy — skill matching
> still works via regex in that case, just without spaCy's tokenizer.

## Testing Guide

Manual test checklist:

| Step | Expected Result |
|------|------------------|
| Launch app | Landing page shows logo, tagline, "Get Started" only |
| Upload a non-PDF file | Uploader rejects it (type-restricted to PDF) |
| Upload a scanned/image-only PDF | Friendly error: "Couldn't read that PDF..." |
| Upload `sample_resume.pdf` | Skills list appears, "Continue" enables |
| Paste `sample_job_description.txt` contents | "Analyze" enables |
| Click Analyze | Results dashboard shows ATS score, semantic score, matched/missing skills |
| Generate Interview | 5 MCQ + 3 technical + 2 scenario (+ coding if role implies it) |
| Submit interview with blank/partial answers | Evaluation still returns (no crash) |
| Revisit any page via sidebar "Start Over" | Session state fully resets, no stale data |
| Remove `GEMINI_API_KEY` from `.env` | Friendly error shown, not a stack trace |

Automated smoke test (no UI):
```bash
python -m py_compile app.py modules/*.py
```

## Notes on Model Choice

The Gemini model is configurable via `GEMINI_MODEL` in `.env`. It defaults to
**`gemini-flash-latest`** — an alias Google auto-updates to whatever its
current stable Flash model is, so the app doesn't quietly break when a
specific version is retired (e.g. `gemini-2.0-flash` itself is scheduled for
shutdown on June 1, 2026). If you want to pin an exact version instead for
reproducibility, check https://ai.google.dev/gemini-api/docs/models and the
deprecations page first.
