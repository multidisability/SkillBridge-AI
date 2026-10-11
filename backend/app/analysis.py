"""Two-step Gemini analysis with deterministic evidence checks."""

import json
from collections.abc import Callable
from typing import TypeVar

from google import genai
from pydantic import BaseModel, ValidationError

from .models import (
    AnalyzeResponse,
    AssessmentDraft,
    Coverage,
    JobRequirementsDraft,
    LearningDay,
    MatchingDraft,
    RequirementResult,
)
from .prompts import EXTRACTION_PROMPT_V1, MATCHING_PROMPT_V1

T = TypeVar("T", bound=BaseModel)
MODEL = "gemini-3.8-flash"


class AnalysisError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def normalized(value: str) -> str:
    return " ".join(value.split()).casefold()


def quote_in_source(quote: str, source: str) -> bool:
    return bool(quote.strip()) and normalized(quote) in normalized(source)


class GeminiAnalyzer:
    def __init__(self, api_key: str, model: str = MODEL) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _structured_call(self, schema: type[T], instruction: str, data: dict) -> T:
        try:
            response = self.client.interactions.create(
                model=self.model,
                system_instruction=instruction,
                input=json.dumps(data, ensure_ascii=False),
                store=False,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": schema.model_json_schema(),
                },
            )
            return schema.model_validate_json(response.output_text or "")
        except ValidationError as exc:
            raise AnalysisError("INVALID_MODEL_OUTPUT", "Format jawaban AI tidak valid.") from exc
        except AnalysisError:
            raise
        except Exception as exc:
            raise AnalysisError("MODEL_UNAVAILABLE", "Layanan AI sedang tidak tersedia. Coba lagi nanti.") from exc

    def _validated_step(
        self,
        schema: type[T],
        instruction: str,
        data: dict,
        validate: Callable[[T], None],
    ) -> T:
        """Retry once for a bad response, keeping the same source data."""
        for attempt in range(2):
            request_data = data if attempt == 0 else {
                **data,
                "correction": "Jawaban sebelumnya gagal validasi. Salin kutipan persis dan ikuti skema serta ID yang diberikan.",
            }
            try:
                result = self._structured_call(schema, instruction, request_data)
                validate(result)
                return result
            except AnalysisError as exc:
                if exc.code == "MODEL_UNAVAILABLE" or attempt == 1:
                    raise
        raise AssertionError("unreachable")

    def analyze(self, profile_text: str, job_text: str) -> AnalyzeResponse:
        def validate_requirements(result: JobRequirementsDraft) -> None:
            if not result.requirements:
                raise AnalysisError(
                    "NO_REQUIREMENTS",
                    "Tidak ada syarat keterampilan yang jelas dalam lowongan ini.",
                    422,
                )
            if len(result.requirements) > 8:
                raise AnalysisError("INVALID_MODEL_OUTPUT", "AI menghasilkan terlalu banyak syarat.")
            names = [normalized(item.skill) for item in result.requirements]
            if len(set(names)) != len(names) or any(not name for name in names):
                raise AnalysisError("INVALID_MODEL_OUTPUT", "Daftar syarat AI tidak valid.")
            if any(not quote_in_source(item.job_quote, job_text) for item in result.requirements):
                raise AnalysisError("INVALID_MODEL_OUTPUT", "Kutipan lowongan tidak sesuai sumber.")

        extracted = self._validated_step(
            JobRequirementsDraft,
            EXTRACTION_PROMPT_V1,
            {"job_text": job_text},
            validate_requirements,
        )
        indexed = [
            {"requirement_id": f"r{index}", **item.model_dump()}
            for index, item in enumerate(extracted.requirements, 1)
        ]
        expected_ids = {item["requirement_id"] for item in indexed}

        def validate_matching(result: MatchingDraft) -> None:
            actual_ids = [item.requirement_id for item in result.assessments]
            if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
                raise AnalysisError("INVALID_MODEL_OUTPUT", "Pencocokan syarat tidak lengkap.")
            for item in result.assessments:
                if not item.reason.strip():
                    raise AnalysisError("INVALID_MODEL_OUTPUT", "Alasan pencocokan kosong.")
                if item.status == "supported" and not quote_in_source(item.profile_quote, profile_text):
                    raise AnalysisError("INVALID_MODEL_OUTPUT", "Kutipan profil tidak sesuai sumber.")
                if item.status == "not_evidenced" and item.profile_quote.strip():
                    raise AnalysisError("INVALID_MODEL_OUTPUT", "Status dan kutipan profil tidak konsisten.")
            days = [day.day for day in result.learning_plan]
            if sorted(days) != list(range(1, 8)):
                raise AnalysisError("INVALID_MODEL_OUTPUT", "Rencana belajar harus berisi hari 1 sampai 7.")
            if any(not day.focus.strip() or not day.action.strip() or not day.deliverable.strip()
                   for day in result.learning_plan):
                raise AnalysisError("INVALID_MODEL_OUTPUT", "Ada langkah belajar yang kosong.")

        matched = self._validated_step(
            MatchingDraft,
            MATCHING_PROMPT_V1,
            {"profile_text": profile_text, "requirements": indexed},
            validate_matching,
        )
        by_id: dict[str, AssessmentDraft] = {
            item.requirement_id: item for item in matched.assessments
        }
        requirements = [
            RequirementResult(
                requirement_id=item["requirement_id"],
                skill=item["skill"],
                job_quote=item["job_quote"],
                status=by_id[item["requirement_id"]].status,
                profile_quote=by_id[item["requirement_id"]].profile_quote or None,
                reason=by_id[item["requirement_id"]].reason.strip(),
            )
            for item in indexed
        ]
        plan: list[LearningDay] = sorted(matched.learning_plan, key=lambda day: day.day)
        return AnalyzeResponse(
            requirements=requirements,
            coverage=Coverage(
                supported=sum(item.status == "supported" for item in requirements),
                total=len(requirements),
            ),
            learning_plan=plan,
        )
