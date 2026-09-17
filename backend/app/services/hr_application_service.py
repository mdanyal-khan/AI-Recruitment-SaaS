from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.resume import Resume
from app.models.user import User


def get_job_for_company(
    db: Session,
    job_id: UUID,
    company_id: UUID,
) -> Job | None:
    return (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_job_applications(
    db: Session,
    job_id: UUID,
    company_id: UUID,
):
    job = get_job_for_company(
        db=db,
        job_id=job_id,
        company_id=company_id,
    )

    if not job:
        return None, []

    applications = (
        db.query(Application)
        .filter(
            Application.job_id == job.id
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    return job, applications


def get_company_applications(
    db: Session,
    company_id: UUID,
):
    applications = (
        db.query(Application)
        .join(Job, Job.id == Application.job_id)
        .filter(Job.company_id == company_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return applications


def get_candidate_user(
    db: Session,
    candidate: Candidate,
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.id == candidate.user_id
        )
        .first()
    )


def get_application_resume(
    db: Session,
    application: Application,
) -> Resume | None:
    if not application.resume_id:
        return None

    return (
        db.query(Resume)
        .filter(
            Resume.id == application.resume_id
        )
        .first()
    )


def get_latest_match_result(
    db: Session,
    application_id: UUID,
) -> MatchResult | None:
    return (
        db.query(MatchResult)
        .filter(
            MatchResult.application_id == application_id
        )
        .order_by(
            MatchResult.created_at.desc()
        )
        .first()
    )