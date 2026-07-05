from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.recommend import router as recommend_router

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Chess Coach AI", version="0.1.0")

app.include_router(recommend_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CHESS_UI_URL", "http://localhost:5173")],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"ok": True}