"""
Complaint analysis service.
Uses Gemini 2.5 Flash (vision-capable) to analyze an optional image + user text
and generate a structured, neutral incident report.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.models.schemas import ComplaintRequest, ComplaintResponse

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vision-capable model list (must support image input)
# ---------------------------------------------------------------------------
VISION_PRIMARY_MODEL = "gemini-2.0-flash"
VISION_FALLBACK_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
]

# Used when the user did NOT specify a complaint type — AI must classify.
COMPLAINT_SYSTEM_PROMPT_CLASSIFY = """You are an AI assistant for incident reporting.

Input:
- An optional image (visual evidence)
- User text describing what happened

Task:
1. Analyze both inputs together (or just text if no image).
2. Classify the complaint type from ONLY these categories:
   stalking, harassment, touching, accident, beating, following, abusing, other
3. Write a clear, factual report in MAXIMUM 30 WORDS.
4. Do NOT assume intentions. Use neutral language: "appears to", "may indicate".
5. Do NOT identify people by name or appearance.
6. Estimate risk level and your confidence.

Output STRICTLY in JSON (no extra text, no markdown):
{
  "complaint_type": "<one category from the list above>",
  "ai_analysis_written_report": "<max 30 words, neutral and factual>",
  "risk_level": "<low | medium | high>",
  "confidence_level": "<low | medium | high>"
}"""

# Used when the user HAS already chosen the complaint type — AI writes report only.
COMPLAINT_SYSTEM_PROMPT_REPORT_ONLY = """You are an AI assistant for incident reporting.

Input:
- An optional image (visual evidence)
- User text describing what happened
- The complaint type already identified by the victim

Task:
1. Analyze both inputs together (or just text if no image).
2. Accept the provided complaint type as final. Do NOT reclassify.
3. Write a clear, factual report in MAXIMUM 30 WORDS.
4. Do NOT assume intentions. Use neutral language: "appears to", "may indicate".
5. Do NOT identify people by name or appearance.
6. Estimate risk level and your confidence.

Output STRICTLY in JSON (no extra text, no markdown):
{
  "ai_analysis_written_report": "<max 30 words, neutral and factual>",
  "risk_level": "<low | medium | high>",
  "confidence_level": "<low | medium | high>"
}"""


def _extract_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model response: {raw}")
    return json.loads(match.group())


async def analyze_complaint(request: ComplaintRequest) -> ComplaintResponse:
    """
    Analyzes image + text (or text-only) to generate a structured incident report.
    Tries Gemini 2.5 Flash (vision) first, then falls back through other Gemini models.
    """
    # Build the API key list
    api_keys = []
    for key_name in ["GEMINI_API_KEY", "GEMINI_API_KEY2", "GEMINI_API_KEY3"]:
        val = os.getenv(key_name)
        if val:
            api_keys.append(val)

    if not api_keys:
        raise EnvironmentError("No GEMINI_API_KEY found in environment.")

    models_to_try = [VISION_PRIMARY_MODEL] + VISION_FALLBACK_MODELS
    last_exception = None

    # ---------------------------------------------------------------------------
    # Choose prompt + complaint_type logic based on whether user already chose a type
    # ---------------------------------------------------------------------------
    user_chose_type = bool(request.complaint_type and request.complaint_type.strip())

    if user_chose_type:
        # User already selected the type — AI only writes the report
        system_prompt = COMPLAINT_SYSTEM_PROMPT_REPORT_ONLY
        user_text_prompt = (
            f"Victim-chosen complaint type: {request.complaint_type}\n"
            f"User's description: {request.text}"
        )
    else:
        # AI must classify the type from scratch
        system_prompt = COMPLAINT_SYSTEM_PROMPT_CLASSIFY
        user_text_prompt = f"User's description: {request.text}"

    for api_key in api_keys:
        client = genai.Client(api_key=api_key)

        for model_name in models_to_try:
            try:
                # Build contents — include image only if provided
                if request.image:
                    # Decode the base64 string and pass as inline image data
                    image_bytes = base64.b64decode(request.image)
                    contents = [
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg",
                        ),
                        types.Part.from_text(text=user_text_prompt),
                    ]
                else:
                    # Text-only mode
                    contents = user_text_prompt

                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                        max_output_tokens=512,
                    ),
                )

                raw = response.text
                logger.debug("Raw complaint analysis response: %s", raw)

                data = _extract_json(raw)

                return ComplaintResponse(
                    user_id=request.user_id,
                    # If user chose a type, always honour it. Otherwise use AI's classification.
                    complaint_type=request.complaint_type.strip() if user_chose_type else data.get("complaint_type", "other"),
                    user_complaint_written_text=request.text,
                    ai_analysis_written_report=data.get("ai_analysis_written_report", ""),
                    risk_level=data.get("risk_level", "medium"),
                    confidence_level=data.get("confidence_level", "medium"),
                )

            except Exception as e:
                logger.warning(
                    "Complaint analysis failed with model %s (key ...%s): %s. Trying next...",
                    model_name, api_key[-4:] if len(api_key) > 4 else "...", e
                )
                last_exception = e

    raise Exception(
        f"All models and API keys failed for complaint analysis. Last error: {last_exception}"
    )
