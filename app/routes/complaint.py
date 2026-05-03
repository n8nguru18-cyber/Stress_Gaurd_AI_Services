"""
Route: POST /raise-complaint

Accepts image (base64) + text description and returns a structured AI incident report.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ComplaintRequest, ComplaintResponse
from app.services.complaint_service import analyze_complaint

router = APIRouter()


@router.post(
    "/raise-complaint",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    summary="Raise an incident complaint using image + text",
    description=(
        "Upload an optional image (base64) and a text description. "
        "The AI generates a neutral, factual incident report with risk level "
        "and confidence score. Supports: harassment, stalking, touching, "
        "abusing, beating, accident, following, other."
    ),
)
async def raise_complaint(request: ComplaintRequest) -> ComplaintResponse:
    try:
        return await analyze_complaint(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Complaint analysis error: {exc}",
        )
