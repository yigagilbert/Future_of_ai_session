"""Shared setup: load API keys from .env and create the Gemini client."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Free-tier friendly default. Override with GEMINI_MODEL in .env if Google renames models.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_client():
    """Return a Gemini client, or exit with a helpful message if the key is missing."""
    from google import genai
    from google.genai import types

    if not os.getenv("GEMINI_API_KEY"):
        sys.exit(
            "GEMINI_API_KEY is not set.\n"
            "1. Get a free key at https://aistudio.google.com/apikey\n"
            "2. Copy .env.example to .env and paste the key there."
        )
    # Reads GEMINI_API_KEY from the environment. The free tier allows only a few
    # requests per minute, so retry automatically on 429/503 instead of crashing.
    return genai.Client(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=5, initial_delay=2, max_delay=30)
        )
    )
