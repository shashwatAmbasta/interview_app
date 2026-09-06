# Sift AI Interview

A local AI interview workspace that turns PDF and DOCX files into grounded interview questions.

## Run locally

1. Start Redis locally (Docker is the easiest option):

   `docker run --name sift-redis -p 6379:6379 -d redis:7-alpine`

2. Create and activate a virtual environment:

   `py -m venv .venv`
   `.venv\\Scripts\\Activate.ps1`

3. Install dependencies:

   `py -m pip install -r requirements.txt`

4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` for live question generation. Without a key, the app uses a deterministic demo question set so the full UI can still be tested.

5. Start the server:

   `py -m uvicorn app.main:app --reload`

Open http://127.0.0.1:8000.

## Project structure

```text
app/
   main.py                 # FastAPI application and lifespan
   api/routes/             # HTTP route handlers
   core/                   # Settings, JWT security, dependencies
   db/                     # SQLite connection and repositories
   schemas/                # Request and response contracts
   services/               # Auth, Redis sessions, documents, LLM
static/                   # Browser client
data/                     # Runtime SQLite database
```

## Architecture

- `data/interview.db`: SQLite user records and PBKDF2 password hashes.
- Redis: JWT-backed session keys and active interview state, both with an 8-hour TTL.
- JWT: The backend issues the token in an HttpOnly, SameSite cookie. Set `COOKIE_SECURE=true` behind HTTPS.
- OpenAI: backend-only integration using `OPENAI_MODEL` and optional `OPENAI_BASE_URL`, so OpenAI-compatible providers can be used.

The `/health` endpoint reports application and Redis availability.

For production, use a strong `JWT_SECRET`, HTTPS, server-set HttpOnly cookies, a managed Redis instance, and a persistent object store for uploaded documents if retention is required.
