from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.offer import Offer
from app.models.user import User

from app.schemas.offer import OfferResponse


router = APIRouter(
    prefix="/candidate/offers",
    tags=["Candidate Offers"],
)


def get_candidate_for_user(
    db: Session,
    user_id: UUID,
):
    return (
        db.query(Candidate)
        .filter(
            Candidate.user_id == user_id
        )
        .first()
    )


def get_candidate_offer(
    db: Session,
    offer_id: UUID,
    candidate_id: UUID,
):
    return (
        db.query(Offer)
        .join(
            Application,
            Application.id == Offer.application_id,
        )
        .filter(
            Offer.id == offer_id,
            Application.candidate_id == candidate_id,
        )
        .first()
    )


@router.get(
    "",
    response_model=list[OfferResponse],
)
def get_my_offers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_for_user(
        db,
        current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    offers = (
        db.query(Offer)
        .join(
            Application,
            Application.id == Offer.application_id,
        )
        .filter(
            Application.candidate_id == candidate.id
        )
        .order_by(
            Offer.created_at.desc()
        )
        .all()
    )

    return offers


@router.get(
    "/{offer_id}",
    response_model=OfferResponse,
)
def get_my_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_for_user(
        db,
        current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    offer = get_candidate_offer(
        db,
        offer_id,
        candidate.id,
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    return offer


@router.patch(
    "/{offer_id}/accept",
    response_model=OfferResponse,
)
def accept_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_for_user(
        db,
        current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    offer = get_candidate_offer(
        db,
        offer_id,
        candidate.id,
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    if offer.status != "SENT":
        raise HTTPException(
            status_code=400,
            detail="Only SENT offers can be accepted.",
        )

    offer.status = "ACCEPTED"

    application = (
        db.query(Application)
        .filter(
            Application.id == offer.application_id
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    application.status = "HIRED"

    db.commit()
    db.refresh(offer)

    return offer


@router.patch(
    "/{offer_id}/decline",
    response_model=OfferResponse,
)
def decline_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = get_candidate_for_user(
        db,
        current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    offer = get_candidate_offer(
        db,
        offer_id,
        candidate.id,
    )

    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found.",
        )

    if offer.status != "SENT":
        raise HTTPException(
            status_code=400,
            detail="Only SENT offers can be declined.",
        )

    offer.status = "DECLINED"

    application = (
        db.query(Application)
        .filter(
            Application.id == offer.application_id
        )
        .first()
    )

    if application:
        application.status = "REJECTED"

    db.commit()
    db.refresh(offer)

    return offer