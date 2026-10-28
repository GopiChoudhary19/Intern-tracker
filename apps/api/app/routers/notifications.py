from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_current_user
from app.models import Application, Opportunity, SavedSearch, User
from app.schemas import NotificationItem, NotificationsResponse
from app.services import use_demo_store

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationsResponse)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationsResponse:
    if use_demo_store():
        return NotificationsResponse(items=DEMO_STORE.notifications())

    now = datetime.now(UTC)
    notifications: list[NotificationItem] = []

    applications = list(
        db.scalars(
            select(Application)
            .options(joinedload(Application.opportunity).joinedload(Opportunity.organization))
            .where(Application.user_id == current_user.id)
            .order_by(Application.updated_at.desc())
        ).unique().all()
    )

    for item in applications:
        deadline = item.opportunity.deadline_at
        # a deadline that has already passed is not "approaching" - those applications are closed
        if deadline and now <= deadline <= now + timedelta(days=7):
            notifications.append(
                NotificationItem(
                    id=f"deadline-{item.id}",
                    title="Deadline approaching",
                    detail=f"{item.opportunity.title} closes within the next 7 days.",
                )
            )
        if item.next_follow_up_at and item.next_follow_up_at <= now + timedelta(days=2):
            notifications.append(
                NotificationItem(
                    id=f"followup-{item.id}",
                    title="Follow-up due",
                    detail=f"Follow up on {item.opportunity.title} soon to keep momentum going.",
                )
            )

    saved_searches = list(
        db.scalars(
            select(SavedSearch)
            .where(SavedSearch.user_id == current_user.id)
            .order_by(SavedSearch.created_at.desc())
        ).all()
    )
    if saved_searches:
        notifications.append(
            NotificationItem(
                id="saved-searches",
                title="Saved searches ready",
                detail=f"You have {len(saved_searches)} saved searches ready to revisit from your dashboard.",
            )
        )

    profile = current_user.profile
    completion_fields = [
        current_user.college_name,
        current_user.degree,
        current_user.branch,
        current_user.city,
        current_user.country,
        profile.bio if profile else None,
        profile.goals if profile else None,
        profile.github_url if profile else None,
        profile.linkedin_url if profile else None,
    ]
    completed = sum(1 for field in completion_fields if field)
    if completed < 6:
        notifications.append(
            NotificationItem(
                id="profile-tip",
                title="Boost your recommendations",
                detail="Complete more of your profile to improve opportunity matching and reminders.",
            )
        )

    return NotificationsResponse(items=notifications[:8])
