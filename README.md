# Agent Evaluation Platform

Independent platform for registering agent targets, running evaluations, collecting artifacts, and publishing reports, trends, and alerts.

## Quickstart

1. Create a virtual environment.
2. Install Python dependencies with `pip install -e .[dev]`.
3. Copy `.env.example` to `.env`.
4. Start PostgreSQL and MinIO with `docker compose up -d`.
5. Run `uvicorn apps.api.main:app --reload`.
