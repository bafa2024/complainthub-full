# backend/app/core/ai_engine.py

import os
import logging
import json

import openai
from google.cloud import translate_v2 as translate

# === Initialization ===

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    translate_client = translate.Client()
except Exception as e:
    logging.warning("No GCP credentials found; skipping translation: %s", e)
    translate_client = None

# === AI Engine ===

class AIEngine:
    @staticmethod
    def analyze_text(text: str) -> tuple[float, int]:
        """
        Uses OpenAI to analyze sentiment (-1.0 to 1.0) and severity (0–5).
        Falls back to neutral values if parsing fails.
        """
        resp = openai.Completion.create(
            model="text-davinci-003",
            prompt=(
                f"Analyze sentiment (-1 to 1) and severity (0-5) of this text:\n"
                f"'''{text}'''\n"
                "Return as JSON {\"sentiment\":..., \"severity\":...}"
            ),
            max_tokens=60
        )
        try:
            data = json.loads(resp.choices[0].text.strip())
        except Exception:
            data = {"sentiment": 0.0, "severity": 1}
        sentiment = float(data.get("sentiment", 0.0))
        severity = int(data.get("severity", 1))
        return sentiment, severity

    @staticmethod
    def translate_text(text: str, target: str = "en") -> str:
        """
        If the GCP Translate client is available, translates text.
        Otherwise returns the original text.
        """
        if not translate_client:
            return text
        result = translate_client.translate(text, target_language=target)
        return result.get("translatedText", text)
