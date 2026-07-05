# Lichess Rapid Games Analysis / Chess Coach App

A full-stack chess analysis project that imports Lichess rapid games, builds an opening tree in a React UI, and recommends candidate moves using a FastAPI coaching service backed by Stockfish, MongoDB, and Redis caching.

## Features

- Fetch and serve Lichess game data from MongoDB
- Explore a player's opening tree from game history
- Analyze FEN positions with Stockfish
- Rank candidate moves with heuristic and player-context features
- Cache expensive recommendations with Redis
- React/Vite frontend with an interactive chessboard and recommendation panel

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | React, Vite, chess.js, react-chessboard |
| Game API | FastAPI, Motor, MongoDB |
| Coach API | FastAPI, python-chess, Stockfish, PyMongo async, Redis |
| Data tooling | Python, Berserk/Lichess tooling |
| Dev services | Docker Compose, MongoDB, Redis |

## Repository Structure

```text
.
├── chess-ui/                    # React/Vite frontend
├── game-fetch-api/
│   ├── fastapi/                 # Games API: serves MongoDB game records
│   └── coach-ai/                # Recommendation API: Stockfish + Redis cache
├── backend/                     # Scraping and data ingestion utilities
├── data/                        # Local generated data; ignored except .gitkeep
├── docker-compose.yml           # MongoDB, Redis, APIs, and frontend
├── .env.example                 # Example local environment variables
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ if running the frontend outside Docker
- Python 3.11+ if running the backend outside Docker
- Stockfish if running `coach-ai` outside Docker

## Quick Start with Docker

From the repo root:

```bash
docker compose up --build
```

Then open:

- Frontend: <http://localhost:5173>
- Games API: <http://localhost:8000>
- Coach AI health check: <http://localhost:8001/health>
- Coach AI docs: <http://localhost:8001/docs>

Docker Compose starts MongoDB, Redis, the games API, the coach API, and the React frontend.

## Local Development Without Docker

### 1. Start MongoDB and Redis

```bash
docker compose up -d mongo redis
```

### 2. Run the Games API

```bash
cd game-fetch-api/fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

### 3. Run the Coach AI API

```bash
cd game-fetch-api/coach-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

### 4. Run the React UI

```bash
cd chess-ui
npm install
npm run dev
```

## Environment Variables

### Games API

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=chessdb
```

### Coach AI API

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=chess-games
REDIS_URL=redis://localhost:6379/0
STOCKFISH_PATH=/usr/local/bin/stockfish
ENGINE_DEPTH=14
CACHE_TTL_SECONDS=604800
RECOMMENDER_VERSION=heuristic_v1
```

Do not commit real `.env` files. Use `.env.example` files for shared defaults.

## API Overview

### Games API

```http
GET /games/user/{username}
```

Returns stored games for a Lichess username.

### Coach AI API

```http
POST /recommend/position
```

Example request:

```json
{
  "fen": "r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq - 2 2",
  "user_id": "demo-user",
  "rating": 1500,
  "color": "white",
  "max_candidates": 6,
  "use_cache": true,
  "refresh_cache": false,
  "force_recompute": false
}
```

The response includes the recommended move, ranked candidates, and metadata such as cache hit/miss status.

## Redis Caching Strategy

The Coach AI service uses Redis to avoid recalculating expensive Stockfish recommendations for repeated positions.

Cache keys include normalized FEN, user id, rating, candidate count, engine depth, and recommender version.

Useful request flags:

- `use_cache`: read/write cached results
- `refresh_cache`: recompute and overwrite the cached result
- `force_recompute`: bypass cache for this request

## Data Notes

Local generated data is ignored by Git:

```text
data/*
!data/.gitkeep
```

This keeps sample databases, scraped games, and user-specific data out of the public repository.

## GitHub Readiness Checklist

- [ ] Confirm `.env` files are not staged
- [ ] Confirm `venv/`, `.venv/`, `node_modules/`, `__pycache__/`, and `.git/` are not included in uploaded zips
- [ ] Add screenshots or a short GIF to `docs/`
- [ ] Replace hardcoded demo username/rating in the UI with controls or config
- [ ] Add tests for API routes and recommendation scoring

## Future Improvements

- Add frontend controls for username, rating, cache mode, and candidate count
- Add background refresh for stale cached recommendations
- Store durable analysis snapshots separately from Redis cache
- Add CI for linting, backend tests, and frontend build
- Deploy APIs and frontend to a cloud provider

## License

MIT License. Update this section if you choose a different license.
