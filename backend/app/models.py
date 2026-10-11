"""Validated API and model output shapes."""

from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class AnalyzeRequest(BaseModel):
    profile_text: str = Field(min_length=20, max_length=10_000)
    job_text: str = Field(min_length=50, max_length=10_000)

    @field_validator("profile_text", "job_text")
    @classmethod
    def strip_text(cls, value: str, info: ValidationInfo) -> str:
        stripped = value.strip()
        minimum = 20 if info.field_name == "profile_text" else 50
        if len(stripped) < minimum:
            raise ValueError(f"Teks harus berisi minimal {minimum} karakter setelah spasi tepi dihapus.")
        return stripped


class JobRequirementDraft(BaseModel):
    skill: str
    job_quote: str


class JobRequirementsDraft(BaseModel):
    requirements: list[JobRequirementDraft]


class AssessmentDraft(BaseModel):
    requirement_id: str
    status: Literal["supported", "not_evidenced"]
    profile_quote: str
    reason: str


class LearningDay(BaseModel):
    day: int
    focus: str
    action: str
    deliverable: str


class MatchingDraft(BaseModel):
    assessments: list[AssessmentDraft]
    learning_plan: list[LearningDay]


class RequirementResult(BaseModel):
    requirement_id: str
    skill: str
    job_quote: str
    status: Literal["supported", "not_evidenced"]
    profile_quote: str | None
    reason: str


class Coverage(BaseModel):
    supported: int
    total: int


class AnalyzeResponse(BaseModel):
    requirements: list[RequirementResult]
    coverage: Coverage
    learning_plan: list[LearningDay]
    notice: str = (
        "Hasil ini membantu menyusun prioritas belajar, bukan penilaian kelayakan kandidat. "
        "Status 'belum terbukti' berarti bukti tidak ditemukan pada profil yang diberikan."
    )
