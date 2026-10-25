from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from app.config import settings
from app.schemas import (
    AdminFeedbackItem,
    AnalyticsOverviewResponse,
    ApplicationRecord,
    CoverLetterResponse,
    FeedbackSubmissionResponse,
    NotificationItem,
    OpportunityDetail,
    OpportunitySummary,
    ResumeAnalyzeResponse,
    SavedSearchResponse,
    ThreadItem,
    UserProfileResponse,
)


class DemoStore:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        opportunity_seed = [
            {
                "title": "SWE Internship Program",
                "organization": "Google",
                "slug": "google-swe-internship-program",
                "type": "internship",
                "domain": "Backend",
                "mode": "Remote",
                "location_text": "Remote, India",
                "description": "Work on distributed systems, developer tooling, and production backend services.",
                "application_url": "https://careers.google.com/jobs/swe-intern",
                "eligibility_text": "Students graduating in 2027 or 2028 with solid CS fundamentals.",
                "required_skills": ["Python", "Data Structures", "APIs"],
                "tags": ["Remote", "Backend", "Deadline in 3 days"],
                "deadline_at": now + timedelta(days=3),
                "is_verified": True,
                "stipend_min": Decimal(45000),
                "stipend_max": Decimal(65000),
                "currency": "INR",
            },
            {
                "title": "Hack the Future 2026",
                "organization": "Devfolio",
                "slug": "devfolio-hack-the-future-2026",
                "type": "hackathon",
                "domain": "AI",
                "mode": "Hybrid",
                "location_text": "Bengaluru + Remote",
                "description": "Build AI-native products with mentorship from startup operators and engineers.",
                "application_url": "https://devfolio.co/hackathons/hack-the-future",
                "eligibility_text": "Open to student builders and multidisciplinary teams.",
                "required_skills": ["React", "AI", "Pitching"],
                "tags": ["Hackathon", "Team Up", "AI + Web"],
                "deadline_at": now + timedelta(days=10),
                "is_verified": True,
                "stipend_min": None,
                "stipend_max": None,
                "currency": None,
            },
            {
                "title": "AI Research Scholarship",
                "organization": "Open Research Lab",
                "slug": "open-research-lab-ai-research-scholarship",
                "type": "scholarship",
                "domain": "AI",
                "mode": "Remote",
                "location_text": "Remote",
                "description": "Receive mentorship, compute grants, and a stipend to pursue applied AI research.",
                "application_url": "https://openresearch.example/scholarship",
                "eligibility_text": "Students with prior ML or research projects.",
                "required_skills": ["Machine Learning", "Python", "Writing"],
                "tags": ["Scholarship", "Mentorship", "Grant"],
                "deadline_at": now + timedelta(days=14),
                "is_verified": True,
                "stipend_min": Decimal(20000),
                "stipend_max": Decimal(30000),
                "currency": "INR",
            },
            {
                "title": "Product Engineering Intern",
                "organization": "Microsoft",
                "slug": "microsoft-product-engineering-intern",
                "type": "internship",
                "domain": "Product",
                "mode": "Hybrid",
                "location_text": "Hyderabad",
                "description": "Ship end-to-end features across product engineering, APIs, and developer experience.",
                "application_url": "https://careers.microsoft.com/product-eng-intern",
                "eligibility_text": "Strong product sense and full-stack project work.",
                "required_skills": ["TypeScript", "APIs", "Product Thinking"],
                "tags": ["Hybrid", "Product", "Fast-moving team"],
                "deadline_at": now + timedelta(days=8),
                "is_verified": True,
                "stipend_min": Decimal(40000),
                "stipend_max": Decimal(55000),
                "currency": "INR",
            },
            {
                "title": "Cloud Career Launchpad",
                "organization": "AWS Educate",
                "slug": "aws-educate-cloud-career-launchpad",
                "type": "event",
                "domain": "Cloud",
                "mode": "Remote",
                "location_text": "Online",
                "description": "A multi-week workshop series on cloud foundations, deployment, and interviews.",
                "application_url": "https://aws.amazon.com/education/launchpad",
                "eligibility_text": "Open to students interested in cloud careers.",
                "required_skills": ["AWS Basics", "Curiosity"],
                "tags": ["Workshop", "Cloud", "Career Prep"],
                "deadline_at": now + timedelta(days=5),
                "is_verified": True,
                "stipend_min": None,
                "stipend_max": None,
                "currency": None,
            },
            {
                "title": "Design Systems Internship",
                "organization": "Figma",
                "slug": "figma-design-systems-internship",
                "type": "internship",
                "domain": "Design",
                "mode": "Remote",
                "location_text": "Remote, APAC",
                "description": "Contribute to design system components and designer-developer workflows.",
                "application_url": "https://www.figma.com/careers/design-systems-intern",
                "eligibility_text": "Portfolio plus frontend collaboration experience.",
                "required_skills": ["UI Systems", "Figma", "Frontend"],
                "tags": ["Remote", "Design Systems", "Portfolio"],
                "deadline_at": now + timedelta(days=11),
                "is_verified": True,
                "stipend_min": Decimal(35000),
                "stipend_max": Decimal(50000),
                "currency": "INR",
            },
            {
                "title": "Open Source Maintainer Fellowship",
                "organization": "GitHub",
                "slug": "github-open-source-maintainer-fellowship",
                "type": "scholarship",
                "domain": "Backend",
                "mode": "Remote",
                "location_text": "Remote",
                "description": "Support student maintainers building meaningful open-source tools and communities.",
                "application_url": "https://github.com/about/careers/fellowship",
                "eligibility_text": "Active OSS contributions with evidence of ownership.",
                "required_skills": ["Git", "OSS", "Documentation"],
                "tags": ["Open Source", "Fellowship", "Remote"],
                "deadline_at": now + timedelta(days=18),
                "is_verified": True,
                "stipend_min": Decimal(15000),
                "stipend_max": Decimal(25000),
                "currency": "INR",
            },
            {
                "title": "Global Hack Week: AI Agents",
                "organization": "MLH",
                "slug": "mlh-global-hack-week-ai-agents",
                "type": "hackathon",
                "domain": "AI",
                "mode": "Remote",
                "location_text": "Online",
                "description": "A week-long guided build sprint around AI agents, tooling, and demos.",
                "application_url": "https://mlh.io/seasons/2026/events/ai-agents",
                "eligibility_text": "Open to all student hackers.",
                "required_skills": ["JavaScript", "LLM Basics", "Demo Skills"],
                "tags": ["Hackathon", "Remote", "AI Agents"],
                "deadline_at": now + timedelta(days=6),
                "is_verified": True,
                "stipend_min": None,
                "stipend_max": None,
                "currency": None,
            },
            {
                "title": "Campus Product Ambassador",
                "organization": "Notion",
                "slug": "notion-campus-product-ambassador",
                "type": "event",
                "domain": "Product",
                "mode": "Hybrid",
                "location_text": "Campus + Remote",
                "description": "Lead workshops, build campus programs, and learn product-led growth from operators.",
                "application_url": "https://www.notion.so/careers/campus-ambassador",
                "eligibility_text": "Strong communicator with campus leadership potential.",
                "required_skills": ["Community", "Writing", "Product"],
                "tags": ["Campus", "Ambassador", "Leadership"],
                "deadline_at": now + timedelta(days=12),
                "is_verified": True,
                "stipend_min": Decimal(10000),
                "stipend_max": Decimal(15000),
                "currency": "INR",
            },
        ]

        self.user = UserProfileResponse(
            id=uuid4(),
            email=settings.demo_email,
            phone=settings.demo_phone,
            full_name="Priya Sharma",
            college_name="National Institute of Technology",
            degree="B.Tech",
            branch="Computer Science",
            graduation_year=2027,
            city="Bengaluru",
            country="India",
            bio="Student builder focused on backend, AI, and product engineering.",
            goals="Find strong internships and hackathons with mentorship.",
            preferred_domains=["AI", "Backend", "Product"],
            preferred_locations=["Remote", "Hybrid"],
            preferred_opportunity_types=["internship", "hackathon"],
            skills=["Python", "FastAPI", "React", "PostgreSQL"],
            github_url="https://github.com/demo-student",
            linkedin_url="https://linkedin.com/in/demo-student",
            resume_url="https://example.com/resume.pdf",
            onboarding_completed=True,
        )

        self.opportunities: list[OpportunityDetail] = [
            OpportunityDetail(
                id=uuid4(),
                slug=item["slug"],
                title=item["title"],
                organization=item["organization"],
                type=item["type"],
                domain=item["domain"],
                mode=item["mode"],
                location_text=item["location_text"],
                tags=item["tags"],
                deadline_at=item["deadline_at"],
                is_verified=item["is_verified"],
                status="published",
                description=item["description"],
                application_url=item["application_url"],
                eligibility_text=item["eligibility_text"],
                required_skills=item["required_skills"],
                stipend_min=float(item["stipend_min"]) if item["stipend_min"] is not None else None,
                stipend_max=float(item["stipend_max"]) if item["stipend_max"] is not None else None,
                currency=item["currency"],
            )
            for item in opportunity_seed
        ]

        opportunity_by_slug = {item.slug: item for item in self.opportunities}
        self.applications: list[ApplicationRecord] = [
            ApplicationRecord(
                id=uuid4(),
                status="saved",
                applied_at=None,
                next_follow_up_at=now + timedelta(days=1),
                note="Strong backend fit. Apply after polishing resume bullets.",
                opportunity=self.to_summary(opportunity_by_slug["google-swe-internship-program"]),
            ),
            ApplicationRecord(
                id=uuid4(),
                status="applied",
                applied_at=now - timedelta(days=2),
                next_follow_up_at=now + timedelta(days=5),
                note="Submitted referral request through alumni network.",
                opportunity=self.to_summary(opportunity_by_slug["microsoft-product-engineering-intern"]),
            ),
            ApplicationRecord(
                id=uuid4(),
                status="shortlisted",
                applied_at=now - timedelta(days=1),
                next_follow_up_at=None,
                note="Team formation in progress with classmates.",
                opportunity=self.to_summary(opportunity_by_slug["mlh-global-hack-week-ai-agents"]),
            ),
        ]
        self.feedback_items: list[FeedbackSubmissionResponse] = []
        self.saved_searches: list[SavedSearchResponse] = []

    def to_summary(self, opportunity: OpportunityDetail) -> OpportunitySummary:
        return OpportunitySummary(**opportunity.model_dump(exclude={"application_url", "eligibility_text", "required_skills", "stipend_min", "stipend_max", "currency"}))

    def list_opportunities(
        self,
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
    ) -> tuple[int, list[OpportunitySummary]]:
        items = self.opportunities
        if search:
            term = search.lower()
            items = [
                item
                for item in items
                if term in item.title.lower()
                or term in item.organization.lower()
                or term in item.description.lower()
                or term in item.domain.lower()
                or term in (item.location_text or "").lower()
            ]
        if opportunity_type:
            items = [item for item in items if item.type == opportunity_type]
        if mode:
            items = [item for item in items if item.mode.lower() == mode.lower()]
        if verified_only:
            items = [item for item in items if item.is_verified]
        if paid_only:
            items = [item for item in items if item.stipend_min is not None or item.stipend_max is not None]
        if min_stipend is not None:
            items = [
                item
                for item in items
                if (item.stipend_min is not None and item.stipend_min >= min_stipend)
                or (item.stipend_max is not None and item.stipend_max >= min_stipend)
            ]
            
        if deadline_days is not None:
            cutoff = datetime.now(UTC) + timedelta(days=deadline_days)
            items = [item for item in items if item.deadline_at is not None and item.deadline_at <= cutoff]
            
        if sort_by == 'deadline_asc':
            items = sorted(items, key=lambda item: item.deadline_at or datetime.max.replace(tzinfo=UTC))
        elif sort_by == 'stipend_desc':
            items = sorted(items, key=lambda item: item.stipend_max or -1, reverse=True)
        elif sort_by == 'newest':
            pass # In demo store we just leave as default or mock it
        else: # relevance
            items = sorted(items, key=lambda item: item.deadline_at or datetime.max.replace(tzinfo=UTC))
            
        total = len(items)
        return total, [self.to_summary(item) for item in items[skip : skip + limit]]

    def get_opportunity(self, slug: str) -> OpportunityDetail | None:
        for item in self.opportunities:
            if item.slug == slug:
                return item
        return None

    def list_admin_opportunities(self) -> list[OpportunityDetail]:
        return deepcopy(self.opportunities)

    def create_opportunity(self, payload: dict) -> OpportunityDetail:
        slug_base = payload.get("slug") or payload["title"].lower().replace(" ", "-")
        slug = slug_base
        index = 2
        existing_slugs = {item.slug for item in self.opportunities}
        while slug in existing_slugs:
            slug = f"{slug_base}-{index}"
            index += 1

        item = OpportunityDetail(
            id=uuid4(),
            slug=slug,
            title=payload["title"],
            organization=payload["organization"],
            type=payload["type"],
            domain=payload["domain"],
            mode=payload["mode"],
            location_text=payload.get("location_text"),
            tags=payload.get("tags", []),
            deadline_at=payload.get("deadline_at"),
            is_verified=payload.get("is_verified", False),
            status=payload.get("status", "published"),
            description=payload["description"],
            application_url=payload["application_url"],
            eligibility_text=payload.get("eligibility_text"),
            required_skills=payload.get("required_skills", []),
            stipend_min=payload.get("stipend_min"),
            stipend_max=payload.get("stipend_max"),
            currency=payload.get("currency"),
        )
        self.opportunities.insert(0, item)
        return deepcopy(item)

    def update_opportunity(self, opportunity_id: UUID, payload: dict) -> OpportunityDetail:
        for item in self.opportunities:
            if item.id == opportunity_id:
                for field, value in payload.items():
                    if hasattr(item, field):
                        setattr(item, field, value)
                return deepcopy(item)
        raise KeyError("Opportunity not found")

    def delete_opportunity(self, opportunity_id: UUID) -> None:
        remaining = [item for item in self.opportunities if item.id != opportunity_id]
        if len(remaining) == len(self.opportunities):
            raise KeyError("Opportunity not found")
        self.opportunities = remaining

    def update_feedback_status(self, feedback_id: UUID, status: str) -> AdminFeedbackItem:
        for item in self.feedback_items:
            if item.id == feedback_id:
                item.status = status
                return AdminFeedbackItem(
                    id=item.id,
                    category=item.category,
                    message=item.message,
                    name=item.name,
                    email=item.email,
                    status=item.status,
                    created_at=item.created_at,
                    user_id=self.user.id,
                    user_name=self.user.full_name,
                )
        raise KeyError("Feedback not found")

    def get_recommended(self) -> list[OpportunitySummary]:
        preferred_domains = set(self.user.preferred_domains)
        preferred_modes = set(self.user.preferred_locations)
        preferred_types = set(self.user.preferred_opportunity_types)
        preferred_skills = set(self.user.skills)

        def score(item: OpportunityDetail) -> int:
            total = 0
            if item.domain in preferred_domains:
                total += 3
            if item.type in preferred_types:
                total += 2
            if item.mode in preferred_modes:
                total += 2
            total += len(set(item.required_skills).intersection(preferred_skills))
            if item.is_verified:
                total += 1
            return total

        ranked = sorted(
            self.opportunities,
            key=lambda item: (-score(item), item.deadline_at or datetime.max.replace(tzinfo=UTC)),
        )
        return [self.to_summary(item) for item in ranked[:6]]

    def list_applications(self) -> list[ApplicationRecord]:
        return deepcopy(self.applications)

    def create_or_get_application(self, opportunity_id: UUID, status: str, note: str | None) -> ApplicationRecord:
        for item in self.applications:
            if item.opportunity.id == opportunity_id:
                return deepcopy(item)

        opportunity = next((item for item in self.opportunities if item.id == opportunity_id), None)
        if opportunity is None:
            raise KeyError("Opportunity not found")

        record = ApplicationRecord(
            id=uuid4(),
            status=status,
            applied_at=datetime.now(UTC) if status != "saved" else None,
            next_follow_up_at=None,
            note=note,
            opportunity=self.to_summary(opportunity),
        )
        self.applications.insert(0, record)
        return deepcopy(record)

    def update_application(
        self,
        application_id: UUID,
        status: str | None = None,
        note: str | None = None,
        next_follow_up_at: datetime | None = None,
    ) -> ApplicationRecord:
        for item in self.applications:
            if item.id == application_id:
                if status is not None:
                    item.status = status
                    if status != "saved" and item.applied_at is None:
                        item.applied_at = datetime.now(UTC)
                if note is not None:
                    item.note = note
                if next_follow_up_at is not None:
                    item.next_follow_up_at = next_follow_up_at
                return deepcopy(item)
        raise KeyError("Application not found")

    def delete_application(self, application_id: UUID) -> None:
        remaining = [item for item in self.applications if item.id != application_id]
        if len(remaining) == len(self.applications):
            raise KeyError("Application not found")
        self.applications = remaining

    def update_profile(self, payload: dict) -> UserProfileResponse:
        current = self.user.model_dump()
        current.update(payload)
        self.user = UserProfileResponse(**current)
        return self.user

    def analytics(self) -> AnalyticsOverviewResponse:
        return AnalyticsOverviewResponse(
            active_users=1,
            new_opportunities=len(self.opportunities),
            saved_applications=len([item for item in self.applications if item.status == "saved"]),
            applied_applications=len([item for item in self.applications if item.status != "saved"]),
        )

    def create_feedback(
        self, *, category: str, message: str, name: str | None = None, email: str | None = None
    ) -> FeedbackSubmissionResponse:
        submission = FeedbackSubmissionResponse(
            id=uuid4(),
            category=category,
            message=message,
            name=name or self.user.full_name,
            email=email or self.user.email,
            status="new",
            created_at=datetime.now(UTC),
        )
        self.feedback_items.insert(0, submission)
        return submission

    def list_feedback(self) -> list[AdminFeedbackItem]:
        return [
            AdminFeedbackItem(
                id=item.id,
                category=item.category,
                message=item.message,
                name=item.name,
                email=item.email,
                status=item.status,
                created_at=item.created_at,
                user_id=self.user.id,
                user_name=self.user.full_name,
            )
            for item in self.feedback_items
        ]

    def notifications(self) -> list[NotificationItem]:
        return [
            NotificationItem(
                id="notif-1",
                title="Deadline reminder",
                detail="Google SWE Internship closes in 3 days.",
            ),
            NotificationItem(
                id="notif-2",
                title="New recommendation",
                detail="A product engineering internship now matches your profile.",
            ),
        ]

    def list_saved_searches(self) -> list[SavedSearchResponse]:
        return deepcopy(self.saved_searches)

    def create_saved_search(self, payload: dict) -> SavedSearchResponse:
        item = SavedSearchResponse(
            id=uuid4(),
            label=payload["label"],
            search=payload.get("search"),
            type=payload.get("type"),
            mode=payload.get("mode"),
            verified=payload.get("verified", False),
            deadline_days=payload.get("deadline_days"),
            paid_only=payload.get("paid_only", False),
            min_stipend=payload.get("min_stipend"),
            created_at=datetime.now(UTC),
        )
        self.saved_searches.insert(0, item)
        return deepcopy(item)

    def delete_saved_search(self, saved_search_id: UUID) -> None:
        remaining = [item for item in self.saved_searches if item.id != saved_search_id]
        if len(remaining) == len(self.saved_searches):
            raise KeyError("Saved search not found")
        self.saved_searches = remaining

    def threads(self) -> list[ThreadItem]:
        return [
            ThreadItem(
                id="thread-1",
                title="Best AI hackathons to apply for this semester?",
                category="hackathons",
                author_name="Priya Sharma",
            ),
            ThreadItem(
                id="thread-2",
                title="Looking for a backend teammate for MLH Global Hack Week",
                category="general",
                author_name="Arjun Patel",
            ),
        ]

    def resume_analysis(self, opportunity_slug: str | None) -> ResumeAnalyzeResponse:
        opportunity = self.get_opportunity(opportunity_slug) if opportunity_slug else None
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

    def cover_letter(self, opportunity_slug: str) -> CoverLetterResponse:
        opportunity = self.get_opportunity(opportunity_slug)
        title = opportunity.title if opportunity else "this role"
        organization = opportunity.organization if opportunity else "your team"
        return CoverLetterResponse(
            content=(
                f"Dear {organization} team,\n\n"
                f"I am excited to apply for {title}. My recent student projects in backend systems, product execution, "
                "and practical AI have prepared me to contribute quickly while learning from strong mentors.\n\n"
                "I would love to bring a builder mindset, clear communication, and ownership to this opportunity.\n\n"
                "Sincerely,\nPriya Sharma"
            )
        )


DEMO_STORE = DemoStore()
