from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_current_user
from app.models import Application, Opportunity, User
from app.schemas import (
    ApplicationRecord,
    ApplicationsResponse,
    CreateApplicationRequest,
    MessageResponse,
    UpdateApplicationRequest,
)
from app.services import (
    APPLICATION_STATUSES,
    get_applications_for_user,
    to_application_record,
    use_demo_store,
)

router = APIRouter(tags=["applications"])


@router.get("/applications", response_model=ApplicationsResponse)
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationsResponse:
    if use_demo_store():
        return ApplicationsResponse(items=DEMO_STORE.list_applications())
    items = get_applications_for_user(db, current_user.id)
    return ApplicationsResponse(items=[to_application_record(item) for item in items])


@router.post("/applications", response_model=ApplicationRecord, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: CreateApplicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationRecord:
    if payload.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid application status")
    if use_demo_store():
        try:
            return DEMO_STORE.create_or_get_application(payload.opportunity_id, payload.status, payload.note)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found") from None

    opportunity = db.get(Opportunity, payload.opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    existing = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.opportunity_id == payload.opportunity_id,
        )
        .first()
    )
    if existing:
        return to_application_record(existing)

    application = Application(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        status=payload.status,
        note=payload.note,
        applied_at=datetime.now(UTC) if payload.status != "saved" else None,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return to_application_record(application)


@router.patch("/applications/{application_id}", response_model=ApplicationRecord)
def update_application(
    application_id: UUID,
    payload: UpdateApplicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationRecord:
    if payload.status is not None and payload.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid application status")
    if use_demo_store():
        try:
            return DEMO_STORE.update_application(
                application_id,
                status=payload.status,
                note=payload.note,
                next_follow_up_at=payload.next_follow_up_at,
            )
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found") from None

    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(application, field, value)
    if payload.status and payload.status != "saved" and application.applied_at is None:
        application.applied_at = datetime.now(UTC)
    db.add(application)
    db.commit()
    db.refresh(application)
    return to_application_record(application)


@router.delete("/applications/{application_id}", response_model=MessageResponse)
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    if use_demo_store():
        try:
            DEMO_STORE.delete_application(application_id)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found") from None
        return MessageResponse(message="Application removed")
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id)
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    db.delete(application)
    db.commit()
    return MessageResponse(message="Application removed")
