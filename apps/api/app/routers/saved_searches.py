from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_current_user
from app.models import SavedSearch, User
from app.schemas import (
    CreateSavedSearchRequest,
    SavedSearchListResponse,
    SavedSearchResponse,
)
from app.services import use_demo_store

router = APIRouter(tags=["saved-searches"])


@router.get("/saved-searches", response_model=SavedSearchListResponse)
def list_saved_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearchListResponse:
    if use_demo_store():
        return SavedSearchListResponse(items=DEMO_STORE.list_saved_searches())

    items = list(
        db.scalars(
            select(SavedSearch)
            .where(SavedSearch.user_id == current_user.id)
            .order_by(SavedSearch.created_at.desc())
        ).all()
    )
    return SavedSearchListResponse(
        items=[
            SavedSearchResponse(
                id=item.id,
                label=item.label,
                search=item.search,
                type=item.type,
                mode=item.mode,
                verified=item.verified,
                deadline_days=item.deadline_days,
                paid_only=item.paid_only,
                min_stipend=float(item.min_stipend) if item.min_stipend is not None else None,
                created_at=item.created_at,
            )
            for item in items
        ]
    )


@router.post("/saved-searches", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
def create_saved_search(
    payload: CreateSavedSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearchResponse:
    if use_demo_store():
        return DEMO_STORE.create_saved_search(payload.model_dump())

    item = SavedSearch(
        user_id=current_user.id,
        label=payload.label.strip(),
        search=payload.search.strip() if payload.search else None,
        type=payload.type,
        mode=payload.mode,
        verified=payload.verified,
        deadline_days=payload.deadline_days,
        paid_only=payload.paid_only,
        min_stipend=payload.min_stipend,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return SavedSearchResponse(
        id=item.id,
        label=item.label,
        search=item.search,
        type=item.type,
        mode=item.mode,
        verified=item.verified,
        deadline_days=item.deadline_days,
        paid_only=item.paid_only,
        min_stipend=float(item.min_stipend) if item.min_stipend is not None else None,
        created_at=item.created_at,
    )


@router.delete("/saved-searches/{saved_search_id}")
def delete_saved_search(
    saved_search_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if use_demo_store():
        try:
            DEMO_STORE.delete_saved_search(saved_search_id)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found") from None
        return {"message": "Saved search removed"}

    item = db.scalar(select(SavedSearch).where(SavedSearch.id == saved_search_id, SavedSearch.user_id == current_user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found")
    db.delete(item)
    db.commit()
    return {"message": "Saved search removed"}
