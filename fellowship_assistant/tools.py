"""
The tools our Fellowship Assistant can use.

These are ordinary Python functions. Nothing here knows about LLMs.
In Step 2 we describe them to Gemini so it can ask us to call them.
In Step 3 we publish the exact same functions through an MCP server.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import requests

BIBLE_API = "https://bible-api.com"
SUNBIRD_API = "https://api.sunbird.ai"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))

TIMEOUT = 30  # seconds


def get_bible_verse(reference: str, translation: str = "web") -> str:
    """Look up a Bible passage by reference.

    Args:
        reference: A Bible reference such as "John 3:16", "Psalm 23" or "Romans 8:28-30".
        translation: Translation code: "web" (World English Bible, default) or "kjv" (King James).

    Returns:
        The reference followed by the passage text, or an error message.
    """
    try:
        r = requests.get(
            f"{BIBLE_API}/{requests.utils.quote(reference)}",
            params={"translation": translation},
            timeout=TIMEOUT,
        )
        if r.status_code == 404:
            return f"Error: could not find the passage '{reference}'. Check the book name and verse numbers."
        r.raise_for_status()
        data = r.json()
        text = " ".join(data["text"].split())
        return f"{data['reference']} ({translation.upper()}): {text}"
    except requests.RequestException as e:
        return f"Error: the Bible API could not be reached ({e})."


def get_random_verse() -> str:
    """Get one random Bible verse (World English Bible). Useful for 'verse of the day'.

    Returns:
        The reference followed by the verse text.
    """
    try:
        r = requests.get(f"{BIBLE_API}/data/web/random", timeout=TIMEOUT)
        r.raise_for_status()
        v = r.json()["random_verse"]
        text = " ".join(v["text"].split())
        return f"{v['book']} {v['chapter']}:{v['verse']} (WEB): {text}"
    except requests.RequestException as e:
        return f"Error: the Bible API could not be reached ({e})."


def translate_text(text: str, target_language: str, source_language: str = "eng") -> str:
    """Translate text between English and African languages using Sunbird AI (Sunflower model).

    Args:
        text: The text to translate.
        target_language: ISO 639-3 code or name, e.g. "lug" (Luganda), "ach" (Acholi),
            "teo" (Ateso), "lgg" (Lugbara), "nyn" (Runyankole), "swa" (Swahili), "eng" (English).
        source_language: ISO 639-3 code of the input text. Defaults to "eng" (English).

    Returns:
        The translated text, or an error message.
    """
    token = os.getenv("SUNBIRD_API_KEY")
    if not token:
        return "Error: SUNBIRD_API_KEY is not set, so translation is unavailable. Get a free key at https://api.sunbird.ai"
    try:
        r = requests.post(
            f"{SUNBIRD_API}/tasks/translate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_language": source_language,
                "target_language": target_language,
                "text": text,
            },
            timeout=120,  # the model can take a moment on a cold start
        )
        if r.status_code >= 400:
            return f"Error from Sunbird API ({r.status_code}): {r.text[:300]}"
        return r.json()["output"]["translated_text"]
    except requests.RequestException as e:
        return f"Error: the Sunbird API could not be reached ({e})."


def save_devotional(title: str, content: str) -> str:
    """Save a finished devotional as a Markdown file so it can be shared with the fellowship.

    Args:
        title: A short title for the devotional.
        content: The full devotional text in Markdown.

    Returns:
        The path of the saved file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "devotional"
    path = OUTPUT_DIR / f"{date.today().isoformat()}-{slug}.md"
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
    return f"Saved to {path}"


# A handy registry: tool name -> Python function.
ALL_TOOLS = {
    fn.__name__: fn
    for fn in (get_bible_verse, get_random_verse, translate_text, save_devotional)
}
