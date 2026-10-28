from __future__ import annotations

import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import (
    Application,
    AuthSession,
    Opportunity,
    Organization,
    User,
    UserProfile,
)
from app.schemas import (
    ApplicationRecord,
    OpportunityDetail,
    OpportunitySummary,
    UserProfileResponse,
)

APPLICATION_STATUSES = {"saved", "applied", "shortlisted", "rejected", "accepted"}
OPPORTUNITY_STATUSES = {"published", "draft", "archived"}
STORAGE_MODE = "database"


def configure_storage_mode(mode: str) -> None:
    global STORAGE_MODE
    STORAGE_MODE = mode


def use_demo_store() -> bool:
    if settings.demo_mode == "demo":
        return True
    if settings.demo_mode == "database":
        return False
    return STORAGE_MODE == "demo"


def create_schema_and_seed(db: Session) -> None:
    from app.db import Base, engine

    Base.metadata.create_all(bind=engine)
    ensure_global_seed_data(db)


def slugify_text(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "opportunity"


def ensure_global_seed_data(db: Session) -> None:
    existing_opportunity = db.scalar(select(Opportunity.id).limit(1))
    if existing_opportunity is not None:
        return

    organizations = [
        Organization(name="Google", website_url="https://careers.google.com", type="company"),
        Organization(name="Devfolio", website_url="https://devfolio.co", type="platform"),
        Organization(name="Open Research Lab", website_url="https://openresearch.example", type="research"),
        Organization(name="Microsoft", website_url="https://careers.microsoft.com", type="company"),
        Organization(name="AWS Educate", website_url="https://aws.amazon.com/education", type="platform"),
        Organization(name="Figma", website_url="https://www.figma.com/careers", type="company"),
        Organization(name="GitHub", website_url="https://github.com/about/careers", type="company"),
        Organization(name="MLH", website_url="https://mlh.io", type="platform"),
        Organization(name="Notion", website_url="https://www.notion.so/careers", type="company"),
    ]
    db.add_all(organizations)
    db.flush()

    now = datetime.now(UTC)
    opportunities = [
        {
            "organization": "Google",
            "title": "SWE Internship Program",
            "slug": "google-swe-internship-program",
            "type": "internship",
            "domain": "Backend",
            "mode": "Remote",
            "location_text": "Remote, India",
            "description": "Work on distributed systems, developer tooling, and production backend services.",
            "stipend_min": Decimal(45000),
            "stipend_max": Decimal(65000),
            "currency": "INR",
            "application_url": "https://careers.google.com/jobs/swe-intern",
            "canonical_url": "https://careers.google.com/jobs/swe-intern",
            "eligibility_text": "Students graduating in 2027 or 2028 with solid CS fundamentals.",
            "required_skills": ["Python", "Data Structures", "APIs"],
            "tags": ["Remote", "Backend", "Deadline in 3 days"],
            "deadline_at": now + timedelta(days=3),
            "is_verified": True,
        },
        {
            "organization": "Devfolio",
            "title": "Hack the Future 2026",
            "slug": "devfolio-hack-the-future-2026",
            "type": "hackathon",
            "domain": "AI",
            "mode": "Hybrid",
            "location_text": "Bengaluru + Remote",
            "description": "Build AI-native products with mentorship from startup operators and engineers.",
            "stipend_min": None,
            "stipend_max": None,
            "currency": None,
            "application_url": "https://devfolio.co/hackathons/hack-the-future",
            "canonical_url": "https://devfolio.co/hackathons/hack-the-future",
            "eligibility_text": "Open to student builders and multidisciplinary teams.",
            "required_skills": ["React", "AI", "Pitching"],
            "tags": ["Hackathon", "Team Up", "AI + Web"],
            "deadline_at": now + timedelta(days=10),
            "is_verified": True,
        },
        {
            "organization": "Open Research Lab",
            "title": "AI Research Scholarship",
            "slug": "open-research-lab-ai-research-scholarship",
            "type": "scholarship",
            "domain": "AI",
            "mode": "Remote",
            "location_text": "Remote",
            "description": "Receive mentorship, compute grants, and a stipend to pursue applied AI research.",
            "stipend_min": Decimal(20000),
            "stipend_max": Decimal(30000),
            "currency": "INR",
            "application_url": "https://openresearch.example/scholarship",
            "canonical_url": "https://openresearch.example/scholarship",
            "eligibility_text": "Students with prior ML or research projects.",
            "required_skills": ["Machine Learning", "Python", "Writing"],
            "tags": ["Scholarship", "Mentorship", "Grant"],
            "deadline_at": now + timedelta(days=14),
            "is_verified": True,
        },
        {
            "organization": "Microsoft",
            "title": "Product Engineering Intern",
            "slug": "microsoft-product-engineering-intern",
            "type": "internship",
            "domain": "Product",
            "mode": "Hybrid",
            "location_text": "Hyderabad",
            "description": "Ship end-to-end features across product engineering, APIs, and developer experience.",
            "stipend_min": Decimal(40000),
            "stipend_max": Decimal(55000),
            "currency": "INR",
            "application_url": "https://careers.microsoft.com/product-eng-intern",
            "canonical_url": "https://careers.microsoft.com/product-eng-intern",
            "eligibility_text": "Strong product sense and full-stack project work.",
            "required_skills": ["TypeScript", "APIs", "Product Thinking"],
            "tags": ["Hybrid", "Product", "Fast-moving team"],
            "deadline_at": now + timedelta(days=8),
            "is_verified": True,
        },
        {
            "organization": "AWS Educate",
            "title": "Cloud Career Launchpad",
            "slug": "aws-educate-cloud-career-launchpad",
            "type": "event",
            "domain": "Cloud",
            "mode": "Remote",
            "location_text": "Online",
            "description": "A multi-week workshop series on cloud foundations, deployment, and interviews.",
            "stipend_min": None,
            "stipend_max": None,
            "currency": None,
            "application_url": "https://aws.amazon.com/education/launchpad",
            "canonical_url": "https://aws.amazon.com/education/launchpad",
            "eligibility_text": "Open to students interested in cloud careers.",
            "required_skills": ["AWS Basics", "Curiosity"],
            "tags": ["Workshop", "Cloud", "Career Prep"],
            "deadline_at": now + timedelta(days=5),
            "is_verified": True,
        },
        {
            "organization": "Figma",
            "title": "Design Systems Internship",
            "slug": "figma-design-systems-internship",
            "type": "internship",
            "domain": "Design",
            "mode": "Remote",
            "location_text": "Remote, APAC",
            "description": "Contribute to design system components and designer-developer workflows.",
            "stipend_min": Decimal(35000),
            "stipend_max": Decimal(50000),
            "currency": "INR",
            "application_url": "https://www.figma.com/careers/design-systems-intern",
            "canonical_url": "https://www.figma.com/careers/design-systems-intern",
            "eligibility_text": "Portfolio plus frontend collaboration experience.",
            "required_skills": ["UI Systems", "Figma", "Frontend"],
            "tags": ["Remote", "Design Systems", "Portfolio"],
            "deadline_at": now + timedelta(days=11),
            "is_verified": True,
        },
        {
            "organization": "GitHub",
            "title": "Open Source Maintainer Fellowship",
            "slug": "github-open-source-maintainer-fellowship",
            "type": "scholarship",
            "domain": "Backend",
            "mode": "Remote",
            "location_text": "Remote",
            "description": "Support student maintainers building meaningful open-source tools and communities.",
            "stipend_min": Decimal(15000),
            "stipend_max": Decimal(25000),
            "currency": "INR",
            "application_url": "https://github.com/about/careers/fellowship",
            "canonical_url": "https://github.com/about/careers/fellowship",
            "eligibility_text": "Active OSS contributions with evidence of ownership.",
            "required_skills": ["Git", "OSS", "Documentation"],
            "tags": ["Open Source", "Fellowship", "Remote"],
            "deadline_at": now + timedelta(days=18),
            "is_verified": True,
        },
        {
            "organization": "MLH",
            "title": "Global Hack Week: AI Agents",
            "slug": "mlh-global-hack-week-ai-agents",
            "type": "hackathon",
            "domain": "AI",
            "mode": "Remote",
            "location_text": "Online",
            "description": "A week-long guided build sprint around AI agents, tooling, and demos.",
            "stipend_min": None,
            "stipend_max": None,
            "currency": None,
            "application_url": "https://mlh.io/seasons/2026/events/ai-agents",
            "canonical_url": "https://mlh.io/seasons/2026/events/ai-agents",
            "eligibility_text": "Open to all student hackers.",
            "required_skills": ["JavaScript", "LLM Basics", "Demo Skills"],
            "tags": ["Hackathon", "Remote", "AI Agents"],
            "deadline_at": now + timedelta(days=6),
            "is_verified": True,
        },
        {
            "organization": "Notion",
            "title": "Campus Product Ambassador",
            "slug": "notion-campus-product-ambassador",
            "type": "event",
            "domain": "Product",
            "mode": "Hybrid",
            "location_text": "Campus + Remote",
            "description": "Lead workshops, build campus programs, and learn product-led growth from operators.",
            "stipend_min": Decimal(10000),
            "stipend_max": Decimal(15000),
            "currency": "INR",
            "application_url": "https://www.notion.so/careers/campus-ambassador",
            "canonical_url": "https://www.notion.so/careers/campus-ambassador",
            "eligibility_text": "Strong communicator with campus leadership potential.",
            "required_skills": ["Community", "Writing", "Product"],
            "tags": ["Campus", "Ambassador", "Leadership"],
            "deadline_at": now + timedelta(days=12),
            "is_verified": True,
        },
    ]

    organizations_by_name = {organization.name: organization for organization in organizations}
    created_opportunities: list[Opportunity] = []
    for item in opportunities:
        created_opportunities.append(
            Opportunity(
                organization=organizations_by_name[item["organization"]],
                title=item["title"],
                slug=item["slug"],
                type=item["type"],
                domain=item["domain"],
                mode=item["mode"],
                location_text=item["location_text"],
                description=item["description"],
                stipend_min=item["stipend_min"],
                stipend_max=item["stipend_max"],
                currency=item["currency"],
                application_url=item["application_url"],
                canonical_url=item["canonical_url"],
                eligibility_text=item["eligibility_text"],
                required_skills=item["required_skills"],
                tags=item["tags"],
                deadline_at=item["deadline_at"],
                is_verified=item["is_verified"],
            )
        )
    db.add_all(created_opportunities)
    db.commit()


def hash_otp(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def mask_identifier(*, email: str | None = None, phone: str | None = None) -> str:
    if email:
        local, _, domain = email.partition("@")
        prefix = local[:2] if len(local) > 2 else local[:1]
        return f"{prefix}{'*' * max(len(local) - len(prefix), 1)}@{domain}"
    if phone:
        return f"{'*' * max(len(phone) - 2, 1)}{phone[-2:]}"
    return "your account"


def build_default_name(*, email: str | None = None, phone: str | None = None, full_name: str | None = None) -> str:
    if full_name and full_name.strip():
        return full_name.strip()
    if email:
        candidate = email.split("@", 1)[0].replace(".", " ").replace("_", " ").strip()
        if candidate:
            return " ".join(part.capitalize() for part in candidate.split())
    if phone:
        return f"Student {phone[-4:]}"
    return "New Student"


def create_session(db: Session, user: User, provider: str = "otp") -> AuthSession:
    session = AuthSession(
        user_id=user.id,
        token=f"itrk_{secrets.token_urlsafe(32)}",
        provider=provider,
        expires_at=datetime.now(UTC) + timedelta(days=settings.auth_session_ttl_days),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def revoke_session_by_token(db: Session, token: str) -> bool:
    session = db.scalar(select(AuthSession).where(AuthSession.token == token, AuthSession.revoked_at.is_(None)))
    if session is None:
        return False
    session.revoked_at = datetime.now(UTC)
    db.add(session)
    db.commit()
    return True


def get_user_by_identifier(db: Session, *, email: str | None = None, phone: str | None = None) -> User | None:
    if email:
        return db.scalar(select(User).options(joinedload(User.profile)).where(User.email == email))
    if phone:
        return db.scalar(select(User).options(joinedload(User.profile)).where(User.phone == phone))
    return None


def create_user_with_profile(
    db: Session,
    *,
    email: str | None = None,
    phone: str | None = None,
    full_name: str | None = None,
) -> User:
    user = User(
        email=email,
        phone=phone,
        full_name=build_default_name(email=email, phone=phone, full_name=full_name),
    )
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id, onboarding_completed=False))
    db.commit()
    return db.scalar(select(User).options(joinedload(User.profile)).where(User.id == user.id))


def to_opportunity_summary(opportunity: Opportunity) -> OpportunitySummary:
    organization_name = opportunity.organization.name if opportunity.organization else "Unknown"
    return OpportunitySummary(
        id=opportunity.id,
        slug=opportunity.slug,
        title=opportunity.title,
        organization=organization_name,
        type=opportunity.type,
        domain=opportunity.domain,
        mode=opportunity.mode,
        location_text=opportunity.location_text,
        tags=opportunity.tags or [],
        deadline_at=opportunity.deadline_at,
        is_verified=opportunity.is_verified,
        status=opportunity.status,
        description=opportunity.description,
    )


def to_opportunity_detail(opportunity: Opportunity) -> OpportunityDetail:
    summary = to_opportunity_summary(opportunity)
    return OpportunityDetail(
        **summary.model_dump(),
        application_url=opportunity.application_url,
        eligibility_text=opportunity.eligibility_text,
        required_skills=opportunity.required_skills or [],
        stipend_min=float(opportunity.stipend_min) if opportunity.stipend_min is not None else None,
        stipend_max=float(opportunity.stipend_max) if opportunity.stipend_max is not None else None,
        currency=opportunity.currency,
    )


def to_application_record(application: Application) -> ApplicationRecord:
    return ApplicationRecord(
        id=application.id,
        status=application.status,
        applied_at=application.applied_at,
        next_follow_up_at=application.next_follow_up_at,
        note=application.note,
        opportunity=to_opportunity_summary(application.opportunity),
    )


def to_user_profile_response(user: User) -> UserProfileResponse:
    profile = user.profile
    return UserProfileResponse(
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
        bio=profile.bio if profile else None,
        goals=profile.goals if profile else None,
        preferred_domains=profile.preferred_domains if profile else [],
        preferred_locations=profile.preferred_locations if profile else [],
        preferred_opportunity_types=profile.preferred_opportunity_types if profile else [],
        skills=profile.skills if profile else [],
        github_url=profile.github_url if profile else None,
        linkedin_url=profile.linkedin_url if profile else None,
        resume_url=profile.resume_url if profile else None,
        onboarding_completed=profile.onboarding_completed if profile else False,
    )


def get_or_create_profile(user: User, db: Session) -> UserProfile:
    if user.profile is None:
        user.profile = UserProfile(user_id=user.id)
        db.add(user.profile)
        db.flush()
    return user.profile


def list_opportunities(
    db: Session,
    search: str | None = None,
    opportunity_type: str | None = None,
    mode: str | None = None,
    verified_only: bool = False,
    deadline_days: int | None = None,
    paid_only: bool = False,
    min_stipend: float | None = None,
    sort_by: str = "relevance",
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, list[Opportunity]]:
    from sqlalchemy import func
    
    query = (
        select(Opportunity)
        .options(joinedload(Opportunity.organization))
        .where(Opportunity.status == "published")
    )
    if search:
        like = f"%{search.strip()}%"
        query = query.where(
            or_(
                Opportunity.title.ilike(like),
                Opportunity.organization.has(Organization.name.ilike(like)),
                Opportunity.description.ilike(like),
                Opportunity.domain.ilike(like),
                Opportunity.location_text.ilike(like),
            )
        )
    if opportunity_type:
        query = query.where(Opportunity.type == opportunity_type)
    if mode:
        query = query.where(Opportunity.mode.ilike(mode))
    if verified_only:
        query = query.where(Opportunity.is_verified.is_(True))
    if paid_only:
        query = query.where(
            or_(Opportunity.stipend_min.is_not(None), Opportunity.stipend_max.is_not(None))
        )
    if min_stipend is not None:
        query = query.where(
            or_(
                Opportunity.stipend_min >= min_stipend,
                Opportunity.stipend_max >= min_stipend,
            )
        )
    if deadline_days is not None:
        query = query.where(
            Opportunity.deadline_at.is_not(None),
            # "closing within N days" means still open: deadlines already passed are not upcoming
            Opportunity.deadline_at >= datetime.now(UTC),
            Opportunity.deadline_at <= datetime.now(UTC) + timedelta(days=deadline_days),
        )

    count_query = select(func.count(Opportunity.id)).where(query.whereclause) if query.whereclause is not None else select(func.count(Opportunity.id))
    total = db.scalar(count_query) or 0

    if sort_by == 'deadline_asc':
        query = query.order_by(
            case((Opportunity.deadline_at.is_(None), 1), else_=0),
            Opportunity.deadline_at.asc()
        )
    elif sort_by == 'stipend_desc':
        query = query.order_by(
            Opportunity.stipend_max.desc().nulls_last()
        )
    elif sort_by == 'newest':
        query = query.order_by(Opportunity.created_at.desc())
    else: # relevance
        query = query.order_by(
            case((Opportunity.deadline_at.is_(None), 1), else_=0),
            Opportunity.deadline_at.asc(),
            Opportunity.created_at.desc(),
        )
        
    if skip > 0:
        query = query.offset(skip)
    if limit > 0:
        query = query.limit(limit)
    return total, list(db.scalars(query).unique().all())


def folded(values) -> set[str]:
    # profile entries are typed by students ("Python", "Remote"), listings use their own casing
    return {value.strip().casefold() for value in values or [] if value}


def get_recommended_opportunities(db: Session, user: User) -> list[Opportunity]:
    profile = get_or_create_profile(user, db)
    query = (
        select(Opportunity)
        .options(joinedload(Opportunity.organization))
        .where(Opportunity.status == "published")
        # closed listings used to be recommended first, because ties are broken by the soonest deadline
        .where(or_(Opportunity.deadline_at.is_(None), Opportunity.deadline_at >= datetime.now(UTC)))
    )
    opportunities = list(db.scalars(query).unique().all())
    domains = folded(profile.preferred_domains)
    types = folded(profile.preferred_opportunity_types)
    modes = folded(profile.preferred_locations)
    skills = folded(profile.skills)

    def score(opportunity: Opportunity) -> int:
        total = 0
        if (opportunity.domain or "").casefold() in domains:
            total += 3
        if (opportunity.type or "").casefold() in types:
            total += 2
        if (opportunity.mode or "").casefold() in modes:
            total += 2
        total += len(folded(opportunity.required_skills) & skills)
        if opportunity.is_verified:
            total += 1
        return total

    opportunities.sort(
        key=lambda item: (
            -score(item),
            item.deadline_at or datetime.max.replace(tzinfo=UTC),
            item.title.lower(),
        )
    )
    return opportunities[:6]


def get_applications_for_user(db: Session, user_id: UUID) -> list[Application]:
    query = (
        select(Application)
        .options(joinedload(Application.opportunity).joinedload(Opportunity.organization))
        .where(Application.user_id == user_id)
        .order_by(Application.updated_at.desc(), Application.created_at.desc())
    )
    return list(db.scalars(query).unique().all())
