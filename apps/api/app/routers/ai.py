from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.models import Opportunity
from app.schemas import (
    CoverLetterRequest,
    CoverLetterResponse,
    ResumeAnalyzeRequest,
    ResumeAnalyzeResponse,
)
from app.services import use_demo_store

router = APIRouter(tags=["ai"])


@router.post("/ai/resume-analyze", response_model=ResumeAnalyzeResponse)
def resume_analyze(payload: ResumeAnalyzeRequest, db: Session = Depends(get_db)) -> ResumeAnalyzeResponse:
    if use_demo_store():
        return DEMO_STORE.resume_analysis(payload.opportunity_slug)
    opportunity = None
    if payload.opportunity_slug:
        opportunity = db.query(Opportunity).filter(Opportunity.slug == payload.opportunity_slug).first()

    focus = opportunity.title if opportunity else "your selected opportunity"
    domain = opportunity.domain if opportunity else "the role"
    return ResumeAnalyzeResponse(
        summary=f"Your resume is close for {focus}. Strengthen impact metrics and make {domain} work easier to scan.",
        highlights=[
            "Add quantified outcomes to project bullets.",
            "Move the most relevant technical skills higher.",
            "Show one clear line that connects your projects to the target role.",
        ],
    )


@router.post("/ai/cover-letter", response_model=CoverLetterResponse)
def cover_letter(payload: CoverLetterRequest, db: Session = Depends(get_db)) -> CoverLetterResponse:
    if use_demo_store():
        return DEMO_STORE.cover_letter(payload.opportunity_slug)
    opportunity = db.query(Opportunity).filter(Opportunity.slug == payload.opportunity_slug).first()
    title = opportunity.title if opportunity else "this role"
    organization = opportunity.organization.name if opportunity and opportunity.organization else "your team"
    return CoverLetterResponse(
        content=(
            f"Dear {organization} team,\n\n"
            f"I am excited to apply for {title}. My recent student projects in backend systems, product execution, "
            "and practical AI have prepared me to contribute quickly while learning from strong mentors.\n\n"
            "I would love to bring a builder mindset, clear communication, and ownership to this opportunity.\n\n"
            "Sincerely,\n[Your Name]"
        )
    )
