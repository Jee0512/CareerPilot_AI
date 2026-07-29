"""
gemini_client.py
-----------------
Thin wrapper around the Google Gemini API using the current `google-genai`
SDK (the old `google-generativeai` package reached end-of-life on Nov 30,
2025 and is no longer supported). Centralizes API key loading, model
selection, JSON-safe parsing, and error handling so the rest of the app
never talks to the SDK directly.
"""

import os
import json
import re
import streamlit as st
from google import genai
from google.genai import types

_CLIENT = None


def _get_api_key() -> str | None:
    """Look for the key in Streamlit Secrets first (deployment), then .env (local dev)."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass  # st.secrets raises if no secrets.toml exists locally — that's fine
    return os.getenv("GEMINI_API_KEY")


def _get_client() -> genai.Client:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "No Gemini API key found. Add GEMINI_API_KEY to a local .env file "
            "or to Streamlit Secrets before running the app."
        )
    _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _get_model_name() -> str:
    try:
        if "GEMINI_MODEL" in st.secrets:
            return st.secrets["GEMINI_MODEL"]
    except Exception:
        pass
    return os.getenv("GEMINI_MODEL", "gemini-flash-latest")


def generate_text(prompt: str, temperature: float = 0.4) -> str:
    """Send a prompt to Gemini and return the raw text response.

    Raises a RuntimeError with a user-friendly message on any failure so
    calling code can show a clean error instead of a stack trace.
    """
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=_get_model_name(),
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        if not response or not getattr(response, "text", None):
            raise RuntimeError("empty response")
        return response.text
    except Exception as exc:  # noqa: BLE001 - we deliberately want a single funnel
        raise RuntimeError(
            f"AI service is temporarily unavailable ({exc}). Please try again in a moment."
        ) from exc


def generate_json(prompt: str, temperature: float = 0.3):
    """Ask Gemini for JSON and parse it robustly. Returns a dict or a list,
    matching whatever top-level JSON structure the model returned.

    Strips markdown code fences and grabs the outermost {...} or [...]
    block if the model adds any stray preamble, then json.loads it.
    """
    raw = generate_text(prompt, temperature=temperature)
    cleaned = re.sub(r"```(json)?", "", raw).strip()

    obj_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    arr_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if obj_match and arr_match:
        cleaned = obj_match.group(0) if obj_match.start() < arr_match.start() else arr_match.group(0)
    elif obj_match:
        cleaned = obj_match.group(0)
    elif arr_match:
        cleaned = arr_match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The AI returned a response we couldn't parse. Please try again."
        ) from exc
