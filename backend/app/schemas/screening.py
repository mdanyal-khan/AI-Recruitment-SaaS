from pydantic import BaseModel


class ScreeningResponse(BaseModel):
    application_id: str
    job_id: str
    candidate_id: str
    resume_id: str
    application_status: str
    match_id: str
    match_score: float
    classification: str
    missing_skills: list
    explanation: dict