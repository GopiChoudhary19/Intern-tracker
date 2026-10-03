# Intern Tracker

Intern Tracker is a modern student opportunity discovery platform for internships, hackathons, coding contests, scholarships, workshops, and tech events.

This repository includes:

- A `Next.js` web frontend scaffold
- A `FastAPI` backend scaffold
- PostgreSQL schema design
- API contract draft
- System architecture
- UI wireframes
- Step-by-step implementation roadmap

## Monorepo Structure

```text
apps/
  api/        FastAPI backend
  web/        Next.js frontend
docs/         Product and engineering deliverables
infra/        Local infrastructure and deployment files
```

## Suggested Stack

- Frontend: Next.js 15, React, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Cache / queues: Redis
- Notifications: Firebase Cloud Messaging, email provider
- Auth: OTP via email/mobile

## Quick Start

This repository is scaffolded for planning and implementation. Dependency installation has not been run in this environment.

1. Install frontend and backend dependencies.
2. Start PostgreSQL and Redis via Docker Compose.
3. Run the web app and API locally.

## 📚 Technical Deliverables

- [System Architecture](docs/system-architecture.md)
- [Database Schema](docs/database-schema.md)
- [API Endpoints Specification](docs/api-endpoints.md)
- [UI Wireframes & Component Specs](docs/ui-wireframes.md)
- [Development Roadmap](docs/development-plan.md)
- [Security & Threat Model](docs/SECURITY.md)

## 📜 License

Licensed under the [MIT License](LICENSE).
