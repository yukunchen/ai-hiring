# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Hiring System - An AI-powered recruitment system that helps HR departments automate the hiring process. It searches candidates from job sites (猎聘, BOSS直聘, LinkedIn), downloads resumes, uses AI to analyze match scores, and sends inquiry emails.

## Commands

### Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=app tests/
```

### Database

The project uses SQLite with SQLAlchemy async. The database file is `aihiring.db` and is auto-created on first run.

## Architecture

```
app/
├── main.py              # FastAPI entry point, mounts static files and routers
├── config.py            # Configuration loading from config.yaml
├── database.py          # Async SQLAlchemy setup
├── models/              # SQLAlchemy ORM models
│   ├── job.py           # Job model (岗位)
│   └── candidate.py     # Candidate model (候选人), FK to Job
├── routers/             # API endpoints
│   ├── jobs.py          # /api/jobs - CRUD for job postings
│   ├── candidates.py    # /api/candidates - CRUD for candidates
│   └── search.py        # /api/search, /api/search/ai - candidate search
└── services/            # Business logic
    ├── scrapers/        # Web scrapers for job sites
    │   ├── factory.py   # ScraperFactory - creates/manages all scrapers
    │   ├── liepin.py    # 猎聘 scraper
    │   ├── zhipin.py    # BOSS直聘 scraper
    │   └── linkedin.py  # LinkedIn scraper
    ├── ai_match.py      # AI resume matching via OpenAI
    ├── ai_search.py     # Combines search + AI matching
    ├── email_generation.py  # AI-powered email content generation
    ├── mailer.py        # SMTP email sending
    └── resume.py        # Resume download and storage
```

### Key Design Patterns

1. **Singleton Services**: All services use a singleton pattern with `get_xxx_service()` functions
2. **Factory Pattern**: `ScraperFactory` creates and manages scrapers for different job sites
3. **Mock Fallback**: AI services return mock data when OpenAI API key is not configured

### Data Model Relationship

- **Job** (1) ──► (N) **Candidate**
- Each candidate belongs to one job via `job_id` foreign key

### Candidate Status Flow

```
pending → contacted → interviewing → offered → hired
    │         │            │            │
    └─────────┴────────────┴────────────┴──► rejected
```

Valid statuses: `pending`, `contacted`, `interviewing`, `offered`, `hired`, `rejected`

## Configuration

Configuration is in `config.yaml`. Environment variables are referenced with `${VAR_NAME}` syntax.

Required environment variables:
- `OPENAI_API_KEY` - For AI matching and email generation
- `SMTP_PASSWORD` - For sending emails

Scraper cookies: Each job site scraper requires cookies from a logged-in session to fetch real data. Without cookies, scrapers return mock data for development.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /api/jobs | List/create jobs |
| GET/PATCH/DELETE | /api/jobs/{id} | Job CRUD |
| GET/POST | /api/candidates | List/create candidates |
| GET/PATCH/DELETE | /api/candidates/{id} | Candidate CRUD |
| GET/POST | /api/search | Basic candidate search |
| GET | /api/search/ai | AI-powered search with match scores |
| GET | /api/search/sources | List available scraper sources |

API docs available at `/docs` (Swagger) and `/redoc` when server is running.
