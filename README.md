# Intern Tracker

![CI](https://github.com/GopiChoudhary19/Intern-tracker/actions/workflows/ci.yml/badge.svg)

A student opportunity discovery platform for internships, hackathons, coding contests, scholarships, workshops and tech events.

## Features

- **Opportunity discovery**: search, filter, sort and compare opportunities, with recommendations based on the student profile
- **Application tracking**: track application status from a dashboard
- **Passwordless login**: email one-time codes (hashed at rest, expiring) sent through the Resend API, with session tokens
- **Security**: per-identifier rate limiting on OTP requests, audit logging of auth events, security headers, trusted-host and CORS middleware
- **Admin tools**: token-protected admin routes for managing opportunities and reviewing user feedback
- **Extras**: saved searches, notifications, community and feedback endpoints, plus resume-analysis and cover-letter helpers
- **Demo mode**: the API runs on an in-memory store with no database (`INTERN_TRACKER_DEMO_MODE=demo`)

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy 2, Pydantic 2 |
| Database | PostgreSQL 16 |
| Infrastructure | Docker Compose, GitHub Actions CI (Ruff lint + frontend build), Render config |

## Repository layout

```text
apps/
  api/        FastAPI backend (routers, models, schemas, services, rate limiter, audit log)
  web/        Next.js frontend (dashboard, opportunities, compare, profile, admin, feedback, help)
docs/         Architecture, database schema, API spec, wireframes, roadmap, threat model
infra/        Docker Compose and Postgres init script
```

## Run locally

```bash
# database
docker compose -f infra/docker-compose.yml up -d postgres

# API (http://localhost:8000/docs)
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload

# or without a database
INTERN_TRACKER_DEMO_MODE=demo uvicorn app.main:app --reload

# web app (http://localhost:3000)
cd apps/web
npm install
npm run dev
```

API routes are served under `/api/v1`. Configuration uses `INTERN_TRACKER_*` environment variables (see `apps/api/app/config.py`).

## Documentation

- [System Architecture](docs/system-architecture.md)
- [Database Schema](docs/database-schema.md)
- [API Endpoints Specification](docs/api-endpoints.md)
- [UI Wireframes & Component Specs](docs/ui-wireframes.md)
- [Development Roadmap](docs/development-plan.md)
- [Security & Threat Model](docs/SECURITY.md)

## License

[MIT](LICENSE)
