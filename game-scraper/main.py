from fastapi import FastAPI
from routes.games import router as games_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Chess Games API")

app.include_router(games_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(os.getenv("CHESS_UI_URL"))],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Chess API running"}