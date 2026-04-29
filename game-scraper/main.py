from fastapi import FastAPI
from routes.games import router as games_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chess Games API")

app.include_router(games_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Chess API running"}