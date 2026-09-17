from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.company import get_current_company
from app.core.database import get_db
from app.services.email_service import send_offer_email
from app.models.user import User
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.services.notification_service import (
    create_notification,
    send_notification_email,
)

from app.schemas.offer import (
    OfferCreate,
    OfferResponse,
    OfferStatusUpdate,
)

from app.services.offer_service import (
    create_offer,
    get_application_for_company,
    get_existing_active_offer,
    get_job_for_application,
    get_offer_for_company,
    get_offers_for_company,
    update_offer_status,
)


router = APIRouter(
    prefix="/offers",
    tags=["Offers"],
)


@router.get(
    "",
    response_model=list[OfferResponse],
)
def list_company_offers(
    current_user: User = Depends(get_current_user),
    current_company=Depends(get_current_company),
    db: Session = Depends(get_db),
):
    return get_offers_for_company(db, current_company.id)


@router.post(
    "",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_offer(
    data: OfferCreate,
    current_user: User = Depends(get_current_user),
    current_company=Depends(get_current_company),
    db: Session = Depends(get_db),
):
    application = get_application_for_company(
        db,
        data.application_id,
        current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    if application.status != "INTERVIEWING":
        raise HTTPException(
            status_code=400,
            detail=(
                "An offer can only be created for an "
                "application in INTERVIEWING status."
            ),
        )

    completed_interview = (
        db.query(Interview)
        .filter(
            Interview.application_id == application.id,
            Interview.status == "COMPLETED",
        )
        .first()
    )

    if not completed_interview:
        raise HTTPException(
            status_code=400,
            detail=(
                "Candidate must have a completed interview before an offer can be created."
            ),
        )

    existing_offer = get_existing_active_offer(
        db,
        application.id,
    )

    if existing_offer:
        raise HTTPException(
            status_code=400,
            detail="An active offer already exists for this application.",
        )

    job = get_job_for_application(
        db,
        application,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    offer = create_offer(
        db=db,
        application=application,
        job=job,
        created_by=current_user.id,
        salary=data.salary,
        currency=data.currency,
        start_date=data.start_date,
        expiration_date=data.expiration_date,
        offer_letter_url=data.offer_letter_url,
        notes=data.notes,
    )

    return offer


@router.get(
    "/{offer_id}",
    response_model=OfferResponse,
)
def get_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company=Depends(get_current_company),
    db: Session = Depends(get_db),
):
    offer = get_offer_for_company(
        db,
        offer_id,
        current_company.id,
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    return offer


@router.patch(
    "/{offer_id}/status",
    response_model=OfferResponse,
)
def change_offer_status(
    offer_id: UUID,
    data: OfferStatusUpdate,
    current_user: User = Depends(get_current_user),
    current_company=Depends(get_current_company),
    db: Session = Depends(get_db),
):
    offer = get_offer_for_company(
        db,
        offer_id,
        current_company.id,
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    allowed_transitions = {
        "PENDING": {
            "SENT",
            "CANCELLED",
        },
        "SENT": {
            "ACCEPTED",
            "DECLINED",
            "EXPIRED",
            "CANCELLED",
        },
        "ACCEPTED": set(),
        "DECLINED": set(),
        "EXPIRED": set(),
        "CANCELLED": set(),
    }

    if data.status not in allowed_transitions.get(
        offer.status,
        set(),
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change offer status from "
                f"{offer.status} to {data.status}."
            ),
        )

    offer = update_offer_status(
        db,
        offer,
        data.status,
    )

    if data.status == "SENT":
        # Candidate email and notification
        app_obj = (
            db.query(Application)
            .filter(Application.id == offer.application_id)
            .first()
        )
        if app_obj:
            cand = (
                db.query(Candidate)
                .filter(Candidate.id == app_obj.candidate_id)
                .first()
            )
            if cand:
                cand_user = (
                    db.query(User)
                    .filter(User.id == cand.user_id)
                    .first()
                )
                if cand_user and cand_user.email:
                    cand_name = (
                        f"{cand_user.first_name or ''} {cand_user.last_name or ''}"
                    ).strip() or "Candidate"

                    email_html = f"""
                    <html>
                    <body>
                        <p>Hello {cand_name},</p>
                        <p><strong>Congratulations!</strong> We are pleased to extend an offer for the position of <strong>{offer.job_title}</strong>.</p>
                        <ul>
                            <li><strong>Salary:</strong> {offer.salary} {offer.currency}</li>
                            <li><strong>Start Date:</strong> {offer.start_date}</li>
                            <li><strong>Expiration Date:</strong> {offer.expiration_date}</li>
                        </ul>
                        <p>Please log in to your candidate portal to accept or decline the offer.</p>
                    </body>
                    </html>
                    """

                    notification = create_notification(
                        db=db,
                        user_id=cand_user.id,
                        notification_type="OFFER",
                        channel="EMAIL",
                        subject=f"Job Offer — {offer.job_title}",
                        message=email_html,
                    )

                    try:
                        send_notification_email(
                            db=db,
                            notification=notification,
                            recipient_email=cand_user.email,
                        )
                    except Exception:
                        pass

    return offer