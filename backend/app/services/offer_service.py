from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
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


def get_job_for_application(
    db: Session,
    application: Application,
):
    return (
        db.query(Job)
        .filter(Job.id == application.job_id)
        .first()
    )


def get_existing_active_offer(
    db: Session,
    application_id: UUID,
):
    return (
        db.query(Offer)
        .filter(
            Offer.application_id == application_id,
            Offer.status.in_(["PENDING", "SENT"]),
        )
        .first()
    )


def get_offer_for_company(
    db: Session,
    offer_id: UUID,
    company_id: UUID,
):
    return (
        db.query(Offer)
        .join(
            Application,
            Application.id == Offer.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Offer.id == offer_id,
            Job.company_id == company_id,
        )
        .first()
    )


def get_offers_for_company(
    db: Session,
    company_id: UUID,
):
    return (
        db.query(Offer)
        .join(
            Application,
            Application.id == Offer.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.company_id == company_id,
        )
        .order_by(
            Offer.created_at.desc(),
        )
        .all()
    )


def get_offers_for_company(
    db: Session,
    company_id: UUID,
):
    return (
        db.query(Offer)
        .join(
            Application,
            Application.id == Offer.application_id,
        )
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Job.company_id == company_id,
        )
        .order_by(
            Offer.created_at.desc(),
        )
        .all()
    )


def create_offer(
    db: Session,
    application: Application,
    job: Job,
    created_by: UUID,
    salary,
    currency: str,
    start_date: date,
    expiration_date: date,
    offer_letter_url: str | None = None,
    notes: str | None = None,
):
    offer = Offer(
        application_id=application.id,
        created_by=created_by,
        job_title=job.title,
        salary=salary,
        currency=currency,
        employment_type=job.employment_type,
        start_date=start_date,
        expiration_date=expiration_date,
        status="PENDING",
        offer_letter_url=offer_letter_url,
        notes=notes,
    )

    db.add(offer)

    application.status = "OFFERED"

    db.commit()
    db.refresh(offer)

    return offer


def update_offer_status(
    db: Session,
    offer: Offer,
    status: str,
):
    offer.status = status

    db.commit()
    db.refresh(offer)

    return offer