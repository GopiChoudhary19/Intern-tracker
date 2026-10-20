from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.demo_store import DEMO_STORE
from app.deps import get_current_user
from app.models import Opportunity, User
from app.schemas import OpportunityDetail, OpportunityListResponse
from app.services import (
    get_recommended_opportunities,
    to_opportunity_detail,
    to_opportunity_summary,
    use_demo_store,
)
from app.services import (
    list_opportunities as fetch_opportunities,
)

router = APIRouter(tags=["opportunities"])


@router.get("/opportunities", response_model=OpportunityListResponse)
def list_opportunities(
    response: Response,
    search: str | None = Query(default=None),
    type: str | None = Query(default=None),
    mode: str | None = Query(default=None),
    verified: bool = Query(default=False),
    deadline_days: int | None = Query(default=None),
    paid_only: bool = Query(default=False),
    min_stipend: float | None = Query(default=None),
    sort_by: str = Query(default="relevance"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, gt=0, le=100),
    db: Session = Depends(get_db),
) -> OpportunityListResponse:
    # Adding short cache header for list query
    response.headers["Cache-Control"] = "public, max-age=60"
    
    if use_demo_store():
        total, items = DEMO_STORE.list_opportunities(
            search=search,
            opportunity_type=type,
            mode=mode,
            verified_only=verified,
            deadline_days=deadline_days,
            paid_only=paid_only,
            min_stipend=min_stipend,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
        )
    else:
        total, opp_items = fetch_opportunities(
            db,
            search=search,
            opportunity_type=type,
            mode=mode,
            verified_only=verified,
            deadline_days=deadline_days,
            paid_only=paid_only,
            min_stipend=min_stipend,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
        )
        items = [to_opportunity_summary(item) for item in opp_items]

    from app.schemas import PaginationMetadata
    metadata = PaginationMetadata(
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        has_next_page=(skip + limit) < total
    )
    return OpportunityListResponse(items=items, metadata=metadata)


@router.get("/opportunities/recommended", response_model=OpportunityListResponse)
def recommended_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OpportunityListResponse:
    if use_demo_store():
        return OpportunityListResponse(items=DEMO_STORE.get_recommended())
    items = get_recommended_opportunities(db, current_user)
    return OpportunityListResponse(items=[to_opportunity_summary(item) for item in items])


@router.get("/opportunities/{slug}", response_model=OpportunityDetail)
def get_opportunity(slug: str, response: Response, db: Session = Depends(get_db)) -> OpportunityDetail:
    # 5 min cache for specific opportunity fetch
    response.headers["Cache-Control"] = "public, max-age=300"
    
    if use_demo_store():
        opportunity = DEMO_STORE.get_opportunity(slug)
        if opportunity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        return opportunity
    opportunity = (
        db.query(Opportunity)
        .options(joinedload(Opportunity.organization))
        .filter(Opportunity.slug == slug, Opportunity.status == "published")
        .first()
    )
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return to_opportunity_detail(opportunity)
