from pydantic import BaseModel


class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None


class ExperienceItem(BaseModel):
    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class CVAnalysis(BaseModel):
    full_name: str = ""
    professional_summary: str = ""
    skills: list[str] = []
    experience_years: float = 0.0
    job_titles: list[str] = []
    education: list[EducationItem] = []
    experience: list[ExperienceItem] = []
    certifications: list[str] = []
    languages: list[str] = []
    location: str = ""
    email: str = ""
    phone: str = ""
