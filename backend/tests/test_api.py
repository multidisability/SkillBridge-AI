"""HTTP contract tests using dependency injection rather than a live key."""

from fastapi.testclient import TestClient

from app.analysis import AnalysisError
from app.main import app, get_analyzer
from app.models import AnalyzeResponse, Coverage, LearningDay, RequirementResult

PROFILE = "Saya membuat dashboard dengan SQL untuk menganalisis penjualan di proyek kampus."
JOB = "Lowongan Data Analyst Intern membutuhkan SQL untuk analisis data dan Python untuk pembersihan data."


class FakeAnalyzer:
    def analyze(self, profile_text: str, job_text: str) -> AnalyzeResponse:
        assert profile_text == PROFILE
        assert job_text == JOB
        return AnalyzeResponse(
            requirements=[
                RequirementResult(
                    requirement_id="r1",
                    skill="SQL",
                    job_quote="SQL untuk analisis data",
                    status="supported",
                    profile_quote="SQL untuk menganalisis penjualan",
                    reason="Ada bukti penggunaan SQL.",
                )
            ],
            coverage=Coverage(supported=1, total=1),
            learning_plan=[
                LearningDay(day=day, focus="Portofolio", action=f"Perbaiki proyek {day}", deliverable=f"Catatan {day}")
                for day in range(1, 8)
            ],
        )


def test_api_response_contract() -> None:
    app.dependency_overrides[get_analyzer] = lambda: FakeAnalyzer()
    try:
        response = TestClient(app).post("/api/analyze", json={"profile_text": PROFILE, "job_text": JOB})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["coverage"] == {"supported": 1, "total": 1}
    assert body["requirements"][0]["status"] == "supported"
    assert len(body["learning_plan"]) == 7


def test_api_rejects_whitespace_only_input() -> None:
    response = TestClient(app).post("/api/analyze", json={"profile_text": " " * 30, "job_text": JOB})
    assert response.status_code == 422


def test_api_explains_missing_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = TestClient(app).post("/api/analyze", json={"profile_text": PROFILE, "job_text": JOB})
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "MISSING_API_KEY"


def test_api_returns_provider_failure_message() -> None:
    class FailingAnalyzer:
        def analyze(self, profile_text: str, job_text: str):
            raise AnalysisError("MODEL_UNAVAILABLE", "Layanan AI sedang tidak tersedia.")

    app.dependency_overrides[get_analyzer] = lambda: FailingAnalyzer()
    try:
        response = TestClient(app).post("/api/analyze", json={"profile_text": PROFILE, "job_text": JOB})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "MODEL_UNAVAILABLE"
