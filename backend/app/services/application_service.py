from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.resume import Resume
from app.models.user import User


def get_candidate(
    db: Session,
    candidate_id: UUID,
) -> Candidate | None:
    """
    Get a candidate by candidate ID.
    """

    return (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )


def get_candidate_by_user_id(
    db: Session,
    user_id: UUID,
) -> Candidate | None:
    """
    Get the candidate profile belonging to a user.
    """

    return (
        db.query(Candidate)
        .filter(Candidate.user_id == user_id)
        .first()
    )


def get_job(
    db: Session,
    job_id: UUID,
) -> Job | None:
    """
    Get a job by job ID.
    """

    return (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )


def get_job_for_application(
    db: Session,
    job_id: UUID,
) -> Job | None:
    """
    Get a published job that is accepting applications.

    Only PUBLISHED jobs can receive applications.
    """

    return (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.status == "PUBLISHED",
        )
        .first()
    )


def get_primary_resume(
    db: Session,
    candidate_id: UUID,
) -> Resume | None:
    """
    Get the candidate's primary resume.

    If multiple primary resumes exist,
    the newest one is returned.
    """

    return (
        db.query(Resume)
        .filter(
            Resume.candidate_id == candidate_id,
            Resume.is_primary.is_(True),
        )
        .order_by(
            Resume.uploaded_at.desc()
        )
        .first()
    )


def get_candidate_resume(
    db: Session,
    candidate_id: UUID,
    resume_id: UUID | None = None,
) -> Resume | None:
    """
    Get a candidate's resume.

    If resume_id is provided:
        return that specific resume belonging
        to the candidate.

    Otherwise:
        return the candidate's primary resume.
    """

    query = (
        db.query(Resume)
        .filter(
            Resume.candidate_id == candidate_id
        )
    )

    if resume_id:
        query = query.filter(
            Resume.id == resume_id
        )
    else:
        query = query.filter(
            Resume.is_primary.is_(True)
        )

    return (
        query
        .order_by(
            Resume.uploaded_at.desc()
        )
        .first()
    )


def get_existing_application(
    db: Session,
    job_id: UUID,
    candidate_id: UUID,
) -> Application | None:
    """
    Check whether the candidate has already
    applied for this job.
    """

    return (
        db.query(Application)
        .filter(
            Application.job_id == job_id,
            Application.candidate_id == candidate_id,
        )
        .first()
    )


def check_existing_application(
    db: Session,
    job_id: UUID,
    candidate_id: UUID,
) -> Application | None:
    """
    Alias for checking an existing application.

    Kept for compatibility with other parts
    of the application service.
    """

    return get_existing_application(
        db=db,
        job_id=job_id,
        candidate_id=candidate_id,
    )


def get_application_for_company(
    db: Session,
    application_id: UUID,
    company_id: UUID,
) -> Application | None:
    """
    Get an application belonging to a company's job.

    This ensures HR users can only access
    applications for their own company.
    """

    return (
        db.query(Application)
        .join(
            Job,
            Application.job_id == Job.id,
        )
        .filter(
            Application.id == application_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_job_applications(
    db: Session,
    job_id: UUID,
    company_id: UUID,
):
    """
    Get all applications for a company's job.

    Returns:
        Application
        Candidate
        User
        MatchResult
    """

    return (
        db.query(
            Application,
            Candidate,
            User,
            MatchResult,
        )
        .join(
            Job,
            Application.job_id == Job.id,
        )
        .join(
            Candidate,
            Application.candidate_id == Candidate.id,
        )
        .join(
            User,
            Candidate.user_id == User.id,
        )
        .outerjoin(
            MatchResult,
            MatchResult.application_id == Application.id,
        )
        .filter(
            Application.job_id == job_id,
            Job.company_id == company_id,
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )


def create_application(
    db: Session,
    job_id: UUID,
    candidate_id: UUID,
    resume_id: UUID | None,
) -> Application:
    """
    Create a new job application.
    """

    application = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        resume_id=resume_id,
        status="APPLIED",
        applied_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def update_application_status(
    db: Session,
    application: Application,
    status: str,
) -> Application:
    """
    Update the status of an application.
    """

    application.status = status

    db.commit()
    db.refresh(application)

    return application