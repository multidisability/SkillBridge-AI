"""Evidence validation and error behavior without external API calls."""

import pytest
from types import SimpleNamespace

from app.analysis import AnalysisError, GeminiAnalyzer, quote_in_source
from app.models import (
    AssessmentDraft,
    JobRequirementDraft,
    JobRequirementsDraft,
    LearningDay,
    MatchingDraft,
)

PROFILE = (
    "Saya membuat dashboard dengan SQL untuk menganalisis penjualan "
    "dan mempresentasikan hasilnya kepada tim produk."
)
JOB = (
    "Lowongan analis data membutuhkan kemampuan SQL untuk menganalisis data "
    "dan kemampuan Python untuk membersihkan dataset."
)


def valid_plan() -> list[LearningDay]:
    return [
        LearningDay(day=day, focus="Python", action=f"Latihan Python tahap {day}", deliverable=f"Catatan latihan {day}")
        for day in range(1, 8)
    ]


def valid_extraction() -> JobRequirementsDraft:
    return JobRequirementsDraft(requirements=[
        JobRequirementDraft(skill="SQL", job_quote="kemampuan SQL untuk menganalisis data"),
        JobRequirementDraft(skill="Python", job_quote="kemampuan Python untuk membersihkan dataset"),
    ])


def valid_matching() -> MatchingDraft:
    return MatchingDraft(
        assessments=[
            AssessmentDraft(
                requirement_id="r1",
                status="supported",
                profile_quote="SQL untuk menganalisis penjualan",
                reason="Profil menunjukkan penggunaan SQL dalam proyek penjualan.",
            ),
            AssessmentDraft(
                requirement_id="r2",
                status="not_evidenced",
                profile_quote="",
                reason="Profil tidak menyebut penggunaan Python.",
            ),
        ],
        learning_plan=valid_plan(),
    )


class StubAnalyzer(GeminiAnalyzer):
    def __init__(self, responses: list[object]) -> None:
        self.responses = iter(responses)
        self.calls = 0

    def _structured_call(self, schema, instruction, data):  # type: ignore[override]
        self.calls += 1
        return next(self.responses)


def test_normalized_quote_check_allows_whitespace_and_case() -> None:
    assert quote_in_source("SQL untuk\nMENGANALISIS penjualan", PROFILE)
    assert not quote_in_source("Python untuk membersihkan dataset", PROFILE)


def test_gemini_call_disables_interaction_storage() -> None:
    captured = {}

    class FakeInteractions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=valid_extraction().model_dump_json())

    analyzer = GeminiAnalyzer.__new__(GeminiAnalyzer)
    analyzer.client = SimpleNamespace(interactions=FakeInteractions())
    analyzer.model = "gemini-3.8-flash"
    result = analyzer._structured_call(JobRequirementsDraft, "instruction", {"job_text": JOB})

    assert result.requirements[0].skill == "SQL"
    assert captured["store"] is False
    assert captured["response_format"]["mime_type"] == "application/json"


def test_two_stage_analysis_returns_verified_evidence_and_seven_days() -> None:
    result = StubAnalyzer([valid_extraction(), valid_matching()]).analyze(PROFILE, JOB)

    assert result.coverage.supported == 1
    assert result.coverage.total == 2
    assert result.requirements[0].profile_quote == "SQL untuk menganalisis penjualan"
    assert result.requirements[1].profile_quote is None
    assert [day.day for day in result.learning_plan] == list(range(1, 8))


def test_bad_job_quote_is_retried_once() -> None:
    invalid = JobRequirementsDraft(requirements=[
        JobRequirementDraft(skill="SQL", job_quote="Pengalaman SQL lima tahun"),
    ])
    analyzer = StubAnalyzer([invalid, valid_extraction(), valid_matching()])

    analyzer.analyze(PROFILE, JOB)
    assert analyzer.calls == 3


def test_fabricated_profile_quote_is_rejected() -> None:
    bad = valid_matching()
    bad.assessments[0].profile_quote = "Saya ahli Python selama sepuluh tahun"
    analyzer = StubAnalyzer([valid_extraction(), bad, bad])

    with pytest.raises(AnalysisError) as error:
        analyzer.analyze(PROFILE, JOB)
    assert error.value.code == "INVALID_MODEL_OUTPUT"
    assert analyzer.calls == 3


def test_no_explicit_job_requirements_is_reported() -> None:
    analyzer = StubAnalyzer([
        JobRequirementsDraft(requirements=[]),
        JobRequirementsDraft(requirements=[]),
    ])

    with pytest.raises(AnalysisError) as error:
        analyzer.analyze(PROFILE, JOB)
    assert error.value.code == "NO_REQUIREMENTS"
    assert error.value.status_code == 422
