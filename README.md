# F1bot

F1bot is a monorepo starter using **Next.js (frontend)** and **FastAPI (backend)** with a Gemini-based Reddit lead scoring pipeline.

## Project Structure

- `frontend/` → Next.js dashboard app
- `backend/` → FastAPI API + Reddit/Gemini services

## Prerequisites

- Node.js 20+
- Python 3.11+

## 1) Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`.

## 2) Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Environment Variables

### Backend (`backend/.env`)

- `GEMINI_API_KEY` → required for Gemini scoring (optional for local mock mode)
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` → required for live Reddit API mode
- `FRONTEND_ORIGIN` → default `http://localhost:3000`

### Frontend (`frontend/.env.local`)

- `NEXT_PUBLIC_API_BASE_URL` → default `http://localhost:8000`

## API Endpoints

- `GET /api/health`
- `POST /api/leads/scan`

`/api/leads/scan` accepts business context + keywords + subreddits and returns scored lead opportunities.

## Notes

- If Reddit or Gemini keys are missing, backend falls back to sample posts + heuristic scoring so you can still build UI fast.
- Gemini flow is designed for `gemini-2.5-flash-lite` (first-pass filtering) and `gemini-2.5-flash` (final scoring).

## Product Planning

- Feature scope and build order: `docs/FEATURES.md`
- Competitor feature intelligence: `docs/COMPETITOR_FEATURES.md`
- Feature comparison matrix: `docs/FEATURE_COMPARISON.md`
