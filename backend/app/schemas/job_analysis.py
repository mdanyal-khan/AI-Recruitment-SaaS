from pydantic import BaseModel


class JobAnalysis(BaseModel):
    job_title: str
    summary: str

    required_skills: list[str]
    preferred_skills: list[str]

    required_experience_years: float
    preferred_experience_years: float

    education_requirements: list[str]

    responsibilities: list[str]

    employment_type: str
    location: str

    certifications: list[str]
    languages: list[str]