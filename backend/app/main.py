from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .routers.investigate import router

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"

app = FastAPI(title="HHGoa Fraud Investigation - Part 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "project": "HHGoa Fraud Investigation",
        "part": "Kashish Part 1",
        "status": "running",
        "mode": "local",
    }


@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard/", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND / "index.html")