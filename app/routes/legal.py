"""
Route: POST /legal-assistance
Provides structured legal advice based on Indian Kanoon API and Groq/Gemini models.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import LegalAssistanceRequest, LegalAssistanceResponse
from app.services.legal_service import generate_legal_advice

router = APIRouter()

@router.post(
    "/legal-assistance",
    response_model=LegalAssistanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get structured legal advice based on Indian Kanoon.",
    description=(
        "Accepts a legal query and optional chat history. "
        "Searches the Indian Kanoon API for relevant Acts/Rules and "
        "returns a structured legal response using Groq/Gemini."
    ),
)
async def legal_assistance(request: LegalAssistanceRequest) -> LegalAssistanceResponse:
    """
    Legal assistance endpoint.
    """
    try:
        return await generate_legal_advice(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Legal service error: {exc}",
        )
