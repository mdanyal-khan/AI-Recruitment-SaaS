from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.interview import Interview
from app.models.job import Job
from app.models.offer import Offer


def get_application_for_company(
    db: Session,
    application_id: UUID,
    company_id: UUID,
):
    return (
        db.query(Application)
        .join(Job, Job.id == Application.job_id)
        .filter(
            Application.id == application_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_latest_completed_interview(
    db: Session,
    application_id: UUID,
):
    return (
        db.query(Interview)
        .filter(
            Interview.application_id == application_id,
            Interview.status == "COMPLETED",
        )
        .order_by(Interview.end_time.desc())
        .first()
    )


def mark_application_hired(
    db: Session,
    application: Application,
):
    application.status = "HIRED"

    db.commit()
    db.refresh(application)

    return application


def mark_application_rejected(
    db: Session,
    application: Application,
):
    application.status = "REJECTED"

    db.commit()
    db.refresh(application)

    return application


def get_offer_for_application(
    db: Session,
    application_id: UUID,
):
    return (
        db.query(Offer)
        .filter(
            Offer.application_id == application_id
        )
        .order_by(Offer.created_at.desc())
        .first()
    )