from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.interview_feedback import InterviewFeedback
from app.models.job import Job
from app.models.user import User


def get_application_for_company(
    db: Session,
    application_id: UUID,
    company_id: UUID,
) -> Application | None:

    return (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_interview_for_company(
    db: Session,
    interview_id: UUID,
    company_id: UUID,
) -> Interview | None:

    return (
        db.query(Interview)
        .join(
            Application,
            Application.id == Interview.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Interview.id == interview_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_active_interview_for_application(
    db: Session,
    application_id: UUID,
) -> Interview | None:

    return (
        db.query(Interview)
        .filter(
            Interview.application_id == application_id,
            Interview.status.in_(
                [
                    "SCHEDULED",
                    "CONFIRMED",
                ]
            ),
        )
        .first()
    )


def create_interview(
    db: Session,
    application: Application,
    scheduled_by: UUID,
    start_time: datetime,
    end_time: datetime,
    timezone: str,
    mode: str,
    meeting_url: str | None,
    location: str | None,
) -> Interview:

    interview = Interview(
        application_id=application.id,
        scheduled_by=scheduled_by,
        start_time=start_time,
        end_time=end_time,
        timezone=timezone,
        mode=mode,
        meeting_url=meeting_url,
        location=location,
        status="SCHEDULED",
    )

    db.add(interview)

    application.status = "INTERVIEWING"

    db.commit()
    db.refresh(interview)

    return interview


def update_interview_status(
    db: Session,
    interview: Interview,
    status: str,
) -> Interview:

    interview.status = status

    db.commit()
    db.refresh(interview)

    return interview


def get_candidate_for_application(
    db: Session,
    application: Application,
) -> Candidate | None:

    return (
        db.query(Candidate)
        .filter(
            Candidate.id == application.candidate_id
        )
        .first()
    )


def get_user_for_candidate(
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


def create_feedback(
    db: Session,
    interview_id: UUID,
    reviewer_id: UUID,
    rating: float | None,
    technical_score: float | None,
    communication_score: float | None,
    culture_score: float | None,
    comments: str | None,
    recommendation: str,
) -> InterviewFeedback:

    feedback = InterviewFeedback(
        interview_id=interview_id,
        reviewer_id=reviewer_id,
        rating=rating,
        technical_score=technical_score,
        communication_score=communication_score,
        culture_score=culture_score,
        comments=comments,
        recommendation=recommendation,
    )

    db.add(feedback)

    db.commit()

    db.refresh(feedback)

    return feedback