"""
The tools our Speak Uganda language buddy can use.

These are ordinary Python functions. Nothing here knows about LLMs.
In Step 2 we describe them to Gemini so it can ask us to call them.
In Step 3 we publish the exact same functions through an MCP server.

APIs used:
  - Sunbird AI (https://api.sunbird.ai): translation and text-to-speech for Ugandan languages
  - Open-Meteo (https://open-meteo.com): free weather, no key. wttr.in is the fallback.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

import requests

SUNBIRD_API = "https://api.sunbird.ai"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
TIMEOUT = 30  # seconds

LANGUAGES = {
    "lug": "Luganda", "ach": "Acholi", "teo": "Ateso", "lgg": "Lugbara",
    "nyn": "Runyankole", "swa": "Swahili", "eng": "English",
}

# WMO weather codes used by Open-Meteo, simplified
WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 80: "rain showers",
    81: "rain showers", 82: "violent rain showers", 95: "thunderstorm",
    96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


# Major towns, so the weather tool still works if the geocoding service is down
TOWNS = {
    "kampala": (0.3476, 32.5825), "entebbe": (0.0512, 32.4637), "jinja": (0.4244, 33.2042),
    "gulu": (2.7746, 32.2990), "lira": (2.2499, 32.8999), "arua": (3.0201, 30.9111),
    "mbarara": (-0.6072, 30.6545), "masaka": (-0.3338, 31.7341), "kabale": (-1.2486, 29.9899),
    "fort portal": (0.6710, 30.2750), "hoima": (1.4331, 31.3524), "mbale": (1.0821, 34.1750),
    "soroti": (1.7146, 33.6111),
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "audio"


def _sunbird_headers() -> dict | None:
    token = os.getenv("SUNBIRD_API_KEY")
    return {"Authorization": f"Bearer {token}"} if token else None


# --- Tool 1: weather ---------------------------------------------------------
def get_weather(city: str, days: int = 3) -> str:
    """Get the weather forecast for a town or city in Uganda.

    Args:
        city: Town or city name, e.g. "Gulu", "Mbarara", "Jinja", "Kampala".
        days: Number of days to forecast, 1 to 7. Defaults to 3.

    Returns:
        One line per day with the conditions, temperatures and chance of rain.
    """
    days = max(1, min(int(days), 7))

    # 1. Find the place: built-in list first, then Open-Meteo geocoding
    key = city.strip().lower()
    if key in TOWNS:
        lat, lon = TOWNS[key]
        place = {"name": city.strip().title(), "latitude": lat, "longitude": lon}
    else:
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "countryCode": "UG"},
                timeout=TIMEOUT,
            ).json()
        except requests.RequestException as e:
            return f"Error: the place lookup service could not be reached ({e})."
        if not geo.get("results"):
            return f"Error: could not find a place called '{city}' in Uganda. Check the spelling."
        place = geo["results"][0]

    # 2. Get the forecast (Open-Meteo, falling back to wttr.in)
    try:
        return _open_meteo(place, days)
    except Exception:
        try:
            return _wttr(place, days)
        except Exception as e:
            return f"Error: no weather service could be reached for '{city}' ({e})."


def _open_meteo(place: dict, days: int) -> str:
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"], "longitude": place["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "Africa/Kampala", "forecast_days": days,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    d = r.json()["daily"]
    lines = [f"Weather for {place['name']}, Uganda:"]
    for i, day in enumerate(d["time"]):
        desc = WEATHER_CODES.get(d["weather_code"][i], "mixed conditions")
        lines.append(
            f"- {day}: {desc}, {d['temperature_2m_min'][i]:.0f}-{d['temperature_2m_max'][i]:.0f}°C, "
            f"{d['precipitation_probability_max'][i]}% chance of rain"
        )
    return "\n".join(lines)


def _wttr(place: dict, days: int) -> str:
    r = requests.get(
        f"https://wttr.in/{place['latitude']:.3f},{place['longitude']:.3f}",
        params={"format": "j1"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    lines = [f"Weather for {place['name']}, Uganda:"]
    for w in r.json()["weather"][:days]:
        rain = max(int(h["chanceofrain"]) for h in w["hourly"])
        desc = w["hourly"][4]["weatherDesc"][0]["value"].strip().lower()
        lines.append(f"- {w['date']}: {desc}, {w['mintempC']}-{w['maxtempC']}°C, {rain}% chance of rain")
    return "\n".join(lines)


# --- Tool 2: translation -----------------------------------------------------
def translate_text(text: str, target_language: str, source_language: str = "eng") -> str:
    """Translate text between English and Ugandan/African languages using Sunbird AI.

    Args:
        text: The text to translate.
        target_language: ISO 639-3 code, e.g. "lug" (Luganda), "ach" (Acholi),
            "teo" (Ateso), "lgg" (Lugbara), "nyn" (Runyankole), "swa" (Swahili), "eng" (English).
        source_language: ISO 639-3 code of the input text. Defaults to "eng" (English).

    Returns:
        The translated text, or an error message.
    """
    headers = _sunbird_headers()
    if not headers:
        return "Error: SUNBIRD_API_KEY is not set, so translation is unavailable. Get a key at https://api.sunbird.ai"
    try:
        r = requests.post(
            f"{SUNBIRD_API}/tasks/translate",
            headers=headers,
            json={"source_language": source_language, "target_language": target_language, "text": text},
            timeout=120,  # the model can take a moment on a cold start
        )
        if r.status_code >= 400:
            return f"Error from Sunbird translate ({r.status_code}): {r.text[:300]}"
        return r.json()["output"]["translated_text"]
    except requests.RequestException as e:
        return f"Error: the Sunbird API could not be reached ({e})."


# --- Tool 3: text-to-speech --------------------------------------------------
def speak_text(text: str, language: str = "lug") -> str:
    """Turn text into spoken audio using Sunbird AI's text-to-speech, and save it as a file.

    Args:
        text: The text to speak. It should already be in the target language
            (translate it first with translate_text).
        language: ISO 639-3 code of the text, e.g. "lug" (Luganda), "ach" (Acholi),
            "teo" (Ateso), "lgg" (Lugbara), "nyn" (Runyankole). Defaults to "lug".
            If no voice exists for a language, an error is returned.

    Returns:
        The path of the saved audio file, or an error message.
    """
    headers = _sunbird_headers()
    if not headers:
        return "Error: SUNBIRD_API_KEY is not set, so speech is unavailable. Get a key at https://api.sunbird.ai"
    try:
        r = requests.post(
            f"{SUNBIRD_API}/tasks/audio/speech",
            headers=headers,
            json={"text": text, "language": language, "response_mode": "url"},
            timeout=180,
        )
        if r.status_code >= 400:
            return f"Error from Sunbird speech ({r.status_code}): {r.text[:300]}"
        info = r.json()
        audio = requests.get(info["audio_url"], timeout=TIMEOUT)
        audio.raise_for_status()
        ext = {"audio/mpeg": ".mp3", "audio/ogg": ".ogg", "audio/x-wav": ".wav"}.get(
            audio.headers.get("Content-Type", "").split(";")[0], ".wav"
        )
        folder = OUTPUT_DIR / "audio"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{language}-{_slug(text)}{ext}"
        path.write_bytes(audio.content)
        return f"Saved {LANGUAGES.get(language, language)} audio ({info.get('voice', 'default voice')}) to {path}"
    except (requests.RequestException, KeyError) as e:
        return f"Error: speech generation failed ({e})."


# --- Tool 4: save the result -------------------------------------------------
def save_phrasebook(title: str, content: str) -> str:
    """Save a finished phrasebook or lesson as a Markdown file.

    Args:
        title: A short title, e.g. "Acholi phrases for Gulu".
        content: The full phrasebook in Markdown (phrases, translations, audio file paths, tips).

    Returns:
        The path of the saved file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{date.today().isoformat()}-{_slug(title)}.md"
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
    return f"Saved to {path}"


# A handy registry: tool name -> Python function.
ALL_TOOLS = {fn.__name__: fn for fn in (get_weather, translate_text, speak_text, save_phrasebook)}
