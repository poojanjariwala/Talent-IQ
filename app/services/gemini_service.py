import json
import re
import asyncio
from typing import Optional, Dict, Any
from app.config import settings
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def _get_model():
    if not settings.GEMINI_API_KEY:
        return None
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(
        settings.GEMINI_MODEL,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

def _build_parse_prompt(raw_text: str) -> str:
    return f"""Extract structured JSON from this resume. Output ONLY JSON.
Resume: {raw_text[:6000]}
"""

def _build_match_prompt(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
    return f"""Evaluate this candidate for the job. Output ONLY JSON.
JOB: {job_data.get('title')}
CANDIDATE: {candidate_data.get('full_name')}
SKILLS: {candidate_data.get('normalized_skills')}
"""

async def enrich_parse_with_gemini(raw_text: str) -> Optional[Dict[str, Any]]:
    if not settings.ENABLE_GEMINI or not settings.GEMINI_API_KEY:
        return None
    try:
        model = _get_model()
        if not model: return None
        response = await model.generate_content_async(_build_parse_prompt(raw_text))
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        return json.loads(json_match.group(0)) if json_match else None
    except Exception as e:
        print(f"❌ Gemini Parse Error: {str(e)}")
    return None

async def enrich_match_with_gemini(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not settings.ENABLE_GEMINI or not settings.GEMINI_API_KEY:
        return None
    try:
        model = _get_model()
        if not model: return None
        response = await model.generate_content_async(_build_match_prompt(candidate_data, job_data))
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        return json.loads(json_match.group(0)) if json_match else None
    except Exception as e:
        print(f"❌ Gemini Match Error: {str(e)}")
    return None
