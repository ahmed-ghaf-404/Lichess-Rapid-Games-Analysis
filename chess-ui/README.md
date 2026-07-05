# Chess Coach UI

React/Vite UI for exploring the user opening tree and requesting coach recommendations.

## Development

```bash
npm install
npm run dev
```

## Recommendation warmup / Redis buffer

The UI can precompute coach recommendations before the board is shown and can keep extending the buffer while the user plays. The preloader calls the existing `coach-ai` recommendation endpoint; if `coach-ai` uses Redis, these calls populate Redis/cache ahead of time.

Create `.env` from `.env.example`:

```env
VITE_GAMES_API_URL=http://localhost:8000
VITE_COACH_AI_URL=http://localhost:8001

VITE_WARMUP_ENABLED=true
VITE_WARMUP_BLOCKING=true
VITE_WARMUP_MAX_POSITIONS=12
VITE_WARMUP_DEPTH=2
VITE_WARMUP_BRANCHING=2

VITE_NEAR_LEAF_THRESHOLD=1
VITE_BACKGROUND_WARMUP_DEPTH=2
VITE_BACKGROUND_WARMUP_BRANCHING=3
VITE_RECOMMENDATION_MAX_CANDIDATES=6
```

### What the controls mean

- **Leaf positions**: how many leaf nodes from the opening tree are used as preload seeds.
- **Startup depth**: how many ply levels are analyzed from each seed. `1` analyzes only the leaf position; `2` analyzes the leaf plus follow-up positions after recommended moves.
- **Branches per leaf**: how many candidate moves to expand at each preload node. Use `2` or `3` to control whether two or three branches are filled.
- **Near-leaf threshold**: when the current opening-tree node is this many moves away from a leaf, background refill starts. `1` means “one position away from a leaf.”
- **Background branches**: how many moves to load when refilling near the frontier. Set this to `3` for “load three more recommended moves.”
- **Wait before showing board**: when enabled, startup preload blocks the board. When disabled, the board appears while Redis fills in the background.

When a recommendation is clicked and played on the board, the UI now starts a background refill from the new FEN so the next side-to-move recommendations are already warming.
