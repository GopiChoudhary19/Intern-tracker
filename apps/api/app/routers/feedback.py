from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_optional_current_user
from app.models import FeedbackSubmission, User
from app.schemas import CreateFeedbackRequest, FeedbackSubmissionResponse
from app.services import use_demo_store

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackSubmissionResponse, status_code=201)
def create_feedback(
    payload: CreateFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> FeedbackSubmissionResponse:
    if use_demo_store():
        return DEMO_STORE.create_feedback(
            category=payload.category,
            message=payload.message.strip(),
            name=payload.name.strip() if payload.name else None,
            email=payload.email.strip().lower() if payload.email else None,
        )

    submission = FeedbackSubmission(
        user_id=current_user.id if current_user else None,
        category=payload.category.strip(),
        message=payload.message.strip(),
        name=(payload.name.strip() if payload.name else None) or (current_user.full_name if current_user else None),
        email=(payload.email.strip().lower() if payload.email else None) or (current_user.email if current_user else None),
        status="new",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return FeedbackSubmissionResponse(
        id=submission.id,
        category=submission.category,
        message=submission.message,
        name=submission.name,
        email=submission.email,
        status=submission.status,
        created_at=submission.created_at,
    )
