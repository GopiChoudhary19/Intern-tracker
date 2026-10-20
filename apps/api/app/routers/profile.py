from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_current_user
from app.models import User
from app.schemas import UpdateProfileRequest, UserProfileResponse
from app.services import get_or_create_profile, to_user_profile_response, use_demo_store

router = APIRouter(tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    if use_demo_store():
        return DEMO_STORE.user
    return to_user_profile_response(current_user)


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    if use_demo_store():
        return DEMO_STORE.update_profile(payload.model_dump(exclude_unset=True))

    profile = get_or_create_profile(current_user, db)
    updates = payload.model_dump(exclude_unset=True)
    user_fields = {
        "full_name",
        "college_name",
        "degree",
        "branch",
        "graduation_year",
        "city",
        "country",
    }
    for field, value in updates.items():
        if field in user_fields:
            setattr(current_user, field, value)
        else:
            setattr(profile, field, value)
    db.add(current_user)
    db.add(profile)
    db.commit()
    db.refresh(current_user)
    return to_user_profile_response(current_user)
