from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.audit_log import log_admin_action
from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import require_admin
from app.models import Application, FeedbackSubmission, Opportunity, Organization, User
from app.schemas import (
    AdminFeedbackItem,
    AdminFeedbackResponse,
    AdminOpportunityPayload,
    AdminUsersResponse,
    AdminUserSummary,
    AnalyticsOverviewResponse,
    OpportunityDetail,
    OpportunityListResponse,
    UpdateFeedbackStatusRequest,
)
from app.services import (
    OPPORTUNITY_STATUSES,
    slugify_text,
    to_opportunity_detail,
    use_demo_store,
)

router = APIRouter(tags=["admin"])


@router.get("/admin/analytics/overview", response_model=AnalyticsOverviewResponse)
def analytics_overview(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> AnalyticsOverviewResponse:
    log_admin_action(admin_id=None, action="READ", resource="ANALYTICS")
    
    if use_demo_store():
        return DEMO_STORE.analytics()
    active_users = db.query(func.count(User.id)).scalar() or 0
    new_opportunities = db.query(func.count(Opportunity.id)).scalar() or 0
    saved_applications = db.query(func.count(Application.id)).filter(Application.status == "saved").scalar() or 0
    applied_applications = (
        db.query(func.count(Application.id)).filter(Application.status != "saved").scalar() or 0
    )
    return AnalyticsOverviewResponse(
        active_users=active_users,
        new_opportunities=new_opportunities,
        saved_applications=saved_applications,
        applied_applications=applied_applications,
    )


@router.get("/admin/users", response_model=AdminUsersResponse)
def list_users(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> AdminUsersResponse:
    if use_demo_store():
        users = DEMO_STORE.list_users()
        log_admin_action(admin_id=None, action="READ", resource="USER", details={"count": len(users)})
        return AdminUsersResponse(items=users)
    
    users = db.query(User).options(joinedload(User.profile)).order_by(User.created_at.desc()).all()
    log_admin_action(admin_id=None, action="READ", resource="USER", details={"count": len(users)})
    
    items: list[AdminUserSummary] = []

    for user in users:
        profile = user.profile
        applications_count = db.query(func.count(Application.id)).filter(Application.user_id == user.id).scalar() or 0
        items.append(
            AdminUserSummary(
                id=user.id,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                college_name=user.college_name,
                degree=user.degree,
                branch=user.branch,
                graduation_year=user.graduation_year,
                city=user.city,
                country=user.country,
                onboarding_completed=profile.onboarding_completed if profile else False,
                applications_count=applications_count,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )

    return AdminUsersResponse(items=items)


@router.get("/admin/feedback", response_model=AdminFeedbackResponse)
def list_feedback(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> AdminFeedbackResponse:
    if use_demo_store():
        return AdminFeedbackResponse(items=DEMO_STORE.list_feedback())

    feedback_items = (
        db.query(FeedbackSubmission)
        .options(joinedload(FeedbackSubmission.user))
        .order_by(FeedbackSubmission.created_at.desc())
        .all()
    )

    return AdminFeedbackResponse(
        items=[
            AdminFeedbackItem(
                id=item.id,
                category=item.category,
                message=item.message,
                name=item.name,
                email=item.email,
                status=item.status,
                created_at=item.created_at,
                user_id=item.user_id,
                user_name=item.user.full_name if item.user else None,
            )
            for item in feedback_items
        ]
    )


@router.get("/admin/opportunities", response_model=OpportunityListResponse)
def list_admin_opportunities(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> OpportunityListResponse:
    if use_demo_store():
        return OpportunityListResponse(items=DEMO_STORE.list_admin_opportunities())

    opportunities = (
        db.query(Opportunity)
        .options(joinedload(Opportunity.organization))
        .order_by(Opportunity.created_at.desc())
        .all()
    )
    return OpportunityListResponse(items=[to_opportunity_detail(item) for item in opportunities])


@router.post("/admin/opportunities", response_model=OpportunityDetail, status_code=status.HTTP_201_CREATED)
def create_admin_opportunity(
    payload: AdminOpportunityPayload,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> OpportunityDetail:
    if payload.status not in OPPORTUNITY_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid opportunity status")
    
    # Validate deadline is in the future if provided
    if payload.deadline_at is not None:
        now = datetime.now(UTC)
        if payload.deadline_at <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deadline must be in the future"
            )

    if use_demo_store():
        return DEMO_STORE.create_opportunity(payload.model_dump())

    organization = db.query(Organization).filter(Organization.name == payload.organization.strip()).first()
    if organization is None:
        organization = Organization(name=payload.organization.strip(), type="company")
        db.add(organization)
        db.flush()

    slug_base = slugify_text(f"{payload.organization}-{payload.title}")
    slug = slug_base
    index = 2
    while db.query(Opportunity.id).filter(Opportunity.slug == slug).first() is not None:
        slug = f"{slug_base}-{index}"
        index += 1

    opportunity = Opportunity(
        organization_id=organization.id,
        title=payload.title.strip(),
        slug=slug,
        type=payload.type.strip().lower(),
        domain=payload.domain.strip(),
        mode=payload.mode.strip(),
        location_text=payload.location_text.strip() if payload.location_text else None,
        description=payload.description.strip(),
        stipend_min=payload.stipend_min,
        stipend_max=payload.stipend_max,
        currency=payload.currency.strip() if payload.currency else None,
        application_url=payload.application_url.strip(),
        canonical_url=payload.application_url.strip(),
        eligibility_text=payload.eligibility_text.strip() if payload.eligibility_text else None,
        required_skills=[item.strip() for item in payload.required_skills if item.strip()],
        tags=[item.strip() for item in payload.tags if item.strip()],
        deadline_at=payload.deadline_at,
        status=payload.status,
        is_verified=payload.is_verified,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return to_opportunity_detail(opportunity)


@router.patch("/admin/opportunities/{opportunity_id}", response_model=OpportunityDetail)
def update_admin_opportunity(
    opportunity_id: UUID,
    payload: AdminOpportunityPayload,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> OpportunityDetail:
    if payload.status not in OPPORTUNITY_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid opportunity status")
    
    # Validate deadline is in the future if provided
    if payload.deadline_at is not None:
        now = datetime.now(UTC)
        if payload.deadline_at <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deadline must be in the future"
            )

    if use_demo_store():
        try:
            return DEMO_STORE.update_opportunity(opportunity_id, payload.model_dump())
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found") from None

    opportunity = (
        db.query(Opportunity)
        .options(joinedload(Opportunity.organization))
        .filter(Opportunity.id == opportunity_id)
        .first()
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    organization = db.query(Organization).filter(Organization.name == payload.organization.strip()).first()
    if organization is None:
        organization = Organization(name=payload.organization.strip(), type="company")
        db.add(organization)
        db.flush()

    opportunity.organization_id = organization.id
    opportunity.title = payload.title.strip()
    opportunity.type = payload.type.strip().lower()
    opportunity.domain = payload.domain.strip()
    opportunity.mode = payload.mode.strip()
    opportunity.location_text = payload.location_text.strip() if payload.location_text else None
    opportunity.description = payload.description.strip()
    opportunity.stipend_min = payload.stipend_min
    opportunity.stipend_max = payload.stipend_max
    opportunity.currency = payload.currency.strip() if payload.currency else None
    opportunity.application_url = payload.application_url.strip()
    opportunity.canonical_url = payload.application_url.strip()
    opportunity.eligibility_text = payload.eligibility_text.strip() if payload.eligibility_text else None
    opportunity.required_skills = [item.strip() for item in payload.required_skills if item.strip()]
    opportunity.tags = [item.strip() for item in payload.tags if item.strip()]
    opportunity.deadline_at = payload.deadline_at
    opportunity.status = payload.status
    opportunity.is_verified = payload.is_verified
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return to_opportunity_detail(opportunity)


@router.delete("/admin/opportunities/{opportunity_id}")
def delete_admin_opportunity(
    opportunity_id: UUID,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if use_demo_store():
        try:
            DEMO_STORE.delete_opportunity(opportunity_id)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found") from None
        return {"message": "Opportunity deleted"}

    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    db.delete(opportunity)
    db.commit()
    return {"message": "Opportunity deleted"}


@router.patch("/admin/feedback/{feedback_id}", response_model=AdminFeedbackItem)
def update_feedback_status(
    feedback_id: UUID,
    payload: UpdateFeedbackStatusRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminFeedbackItem:
    if use_demo_store():
        try:
            return DEMO_STORE.update_feedback_status(feedback_id, payload.status.strip())
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found") from None

    feedback = db.query(FeedbackSubmission).filter(FeedbackSubmission.id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    feedback.status = payload.status.strip()
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return AdminFeedbackItem(
        id=feedback.id,
        category=feedback.category,
        message=feedback.message,
        name=feedback.name,
        email=feedback.email,
        status=feedback.status,
        created_at=feedback.created_at,
        user_id=feedback.user_id,
        user_name=feedback.user.full_name if feedback.user else None,
    )
