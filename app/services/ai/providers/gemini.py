"""
Gemini provider adapter — the only module in the codebase that imports google.genai.

Lazy client construction avoids blocking at import time and lets tests import
app.services.ai without triggering Vertex AI credential resolution.
"""
import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings

_client: "genai.Client | None" = None

MODEL = "gemini-2.5-flash"


def _get_client() -> "genai.Client":
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=settings.gcp_project,
            location=settings.gcp_location,
        )
    return _client


class GeminiProvider:
    """Calls the Gemini generate_content API and returns json.loads(response.text).

    Accepts two content shapes:
    - str or list: passed directly as the `contents` argument (text-only prompts,
      or pre-built parts lists).
    - dict with "audio_bytes" key: unpacked into a types.Part.from_bytes + prompt
      list so callers (AiService) never import google.genai directly.
    """

    def generate_json(self, contents: Any, temperature: float) -> dict:
        if isinstance(contents, dict) and "audio_bytes" in contents:
            audio_part = types.Part.from_bytes(
                data=contents["audio_bytes"],
                mime_type=contents["mime_type"],
            )
            api_contents = [audio_part, contents["prompt"]]
        else:
            api_contents = contents

        response = _get_client().models.generate_content(
            model=MODEL,
            contents=api_contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=temperature,
            ),
        )
        return json.loads(response.text)
