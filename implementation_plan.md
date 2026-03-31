# Talent Intelligence Platform — Streamlit Rebuild Implementation Plan

## Project Structure

```
resume-new(s)/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings / feature flags
│   ├── database.py                # SQLAlchemy engine & session
│   ├── models/                    # SQLAlchemy ORM models
│   ├── schemas/                   # Pydantic models
│   ├── repositories/              # DB access layer
│   ├── services/                  # Business logic
│   ├── tasks/                     # Celery tasks
│   └── routers/                   # FastAPI routers
├── streamlit_app/
│   ├── app.py                     # Main Streamlit entry point
│   ├── state.py                   # Session state helpers
│   ├── pages/                     # Individual page modules
│   ├── components/                # Reusable widgets
│   └── utils/                     # API client + formatters
├── skill_taxonomy/
│   └── taxonomy.json
├── migrations/
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Build Order
1. Config, domain models, Pydantic schemas
2. Database setup
3. Repositories
4. File extraction and parser
5. Skill taxonomy + normalizer
6. Matching engine
7. Audit service + controller pipeline
8. FastAPI routers
9. Celery tasks + Redis
10. Streamlit frontend
11. Gemini enrichment (feature-flagged)
12. Docker + docker-compose
