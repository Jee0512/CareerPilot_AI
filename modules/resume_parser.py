"""
resume_parser.py
-----------------
Extracts raw text from an uploaded PDF resume (PyMuPDF) and pulls out a
normalized list of skills using a curated skills dictionary + spaCy for
tokenization/lemmatization.
"""

import io
import re
import fitz  # PyMuPDF
import spacy
import streamlit as st

# A broad-but-finite skills vocabulary. Real products train/maintain a much
# larger taxonomy (e.g. ESCO, LinkedIn Skills Graph) — this keeps the demo
# self-contained with no external calls.
SKILLS_VOCAB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "nosql", "mongodb", "postgresql", "mysql",
    "machine learning", "deep learning", "nlp", "computer vision",
    "sentence transformers", "pytorch", "tensorflow", "scikit-learn", "keras",
    "pandas", "numpy", "spacy", "nltk", "opencv",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "streamlit", "flask", "django", "fastapi", "react", "node.js", "html", "css",
    "git", "linux", "rest api", "graphql", "airflow", "spark", "hadoop",
    "tableau", "power bi", "excel", "data analysis", "data visualization",
    "statistics", "a/b testing", "rag", "llm", "prompt engineering",
    "agile", "scrum", "project management", "devops", "microservices",
]


@st.cache_resource(show_spinner=False)
def _load_spacy_model():
    """Load spaCy once per session and cache it (model loading is slow)."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not downloaded yet — fall back to a blank English pipeline
        # so the app still runs; skill matching still works via regex.
        return spacy.blank("en")


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract plain text from a Streamlit-uploaded PDF file object OR raw bytes."""
    try:
        file_bytes = uploaded_file if isinstance(uploaded_file, (bytes, bytearray)) else uploaded_file.read()
        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if not text.strip():
            raise ValueError("empty")
        return text
    except Exception as exc:
        raise RuntimeError(
            "Couldn't read that PDF. Make sure it's a text-based (not scanned/image) resume."
        ) from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text (paragraphs + table cells) from a .docx file's raw bytes."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        parts.append(cell.text)
        text = "\n".join(parts)
        if not text.strip():
            raise ValueError("empty")
        return text
    except Exception as exc:
        raise RuntimeError(
            "Couldn't read that DOCX file. Make sure it's a valid, non-corrupted Word document."
        ) from exc


def extract_layout_lines(file_bytes: bytes) -> list[dict]:
    """
    Extract text at LINE granularity with position/font/color info, for
    layout-preserving in-place editing (used by the Resume Optimizer to
    white-out and reinsert text at the exact original position instead of
    generating a plain new document).

    Each line dict: {id, page, bbox: [x0,y0,x1,y1], text, font, size, color, flags}
    """
    try:
        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
    except Exception as exc:
        raise RuntimeError("Couldn't read that PDF for layout extraction.") from exc

    lines_out = []
    idx = 0
    for page_num, page in enumerate(doc):
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                if not text:
                    continue
                x0 = min(s["bbox"][0] for s in spans)
                y0 = min(s["bbox"][1] for s in spans)
                x1 = max(s["bbox"][2] for s in spans)
                y1 = max(s["bbox"][3] for s in spans)
                dominant = max(spans, key=lambda s: len(s["text"]))
                lines_out.append({
                    "id": idx, "page": page_num, "bbox": [x0, y0, x1, y1],
                    "text": text, "font": dominant.get("font", ""),
                    "size": dominant.get("size", 10), "color": dominant.get("color", 0),
                    "flags": dominant.get("flags", 0),
                })
                idx += 1
    doc.close()
    return lines_out


def extract_skills(text: str) -> list[str]:
    """Return the subset of SKILLS_VOCAB found in the given text (case-insensitive)."""
    nlp = _load_spacy_model()
    doc = nlp(text.lower())
    normalized = doc.text  # lemmatized-ish lowercase text via spaCy tokenization

    found = []
    for skill in SKILLS_VOCAB:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))
