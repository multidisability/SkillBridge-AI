"""HTTP API and optional production frontend hosting."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .analysis import AnalysisError, GeminiAnalyzer
from .models import AnalyzeRequest, AnalyzeResponse

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="SkillBridge AI", version="0.1.0")


def get_analyzer() -> GeminiAnalyzer | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return GeminiAnalyzer(api_key) if api_key else None


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest, analyzer: GeminiAnalyzer | None = Depends(get_analyzer)) -> AnalyzeResponse:
    if analyzer is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "MISSING_API_KEY",
                "message": "Gemini API key belum dikonfigurasi di server.",
            },
        )
    try:
        return analyzer.analyze(request.profile_text, request.job_text)
    except AnalysisError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
