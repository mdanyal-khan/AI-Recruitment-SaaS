from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HRApplicationListItem(BaseModel):
    application_id: UUID
    candidate_id: UUID
    candidate_name: str | None
    candidate_email: str | None
    job_id: UUID
    job_title: str
    resume_id: UUID | None
    application_status: str
    match_score: float | None
    classification: str | None
    applied_at: datetime | None = None


class HRApplicationDetail(BaseModel):
    application_id: UUID
    candidate_id: UUID
    candidate_name: str | None
    candidate_email: str | None

    job_id: UUID
    job_title: str

    resume_id: UUID | None
    resume_file_name: str | None
    resume_file_url: str | None

    application_status: str
    applied_at: datetime | None = None

    match_score: float | None
    classification: str | None
    skill_score: float | None
    experience_score: float | None
    education_score: float | None
    keyword_score: float | None

    missing_skills: list
    explanation: dict | None