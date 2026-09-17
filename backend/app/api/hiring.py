from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.company import get_current_company

from app.models.user import User

from app.schemas.hiring import (
    HiringDecisionRequest,
    HiringDecisionResponse,
)

from app.services.hiring_service import (
    get_application_for_company,
    get_latest_completed_interview,
    mark_application_hired,
    mark_application_rejected,
)


router = APIRouter(
    prefix="/hiring",
    tags=["Hiring"],
)


@router.patch(
    "/applications/{application_id}/decision",
    response_model=HiringDecisionResponse,
)
def make_hiring_decision(
    application_id: UUID,
    data: HiringDecisionRequest,
    current_user: User = Depends(get_current_user),
    current_company=Depends(get_current_company),
    db: Session = Depends(get_db),
):
    application = get_application_for_company(
        db,
        application_id,
        current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    decision = data.decision.upper()

    if decision not in {"HIRE", "REJECT"}:
        raise HTTPException(
            status_code=400,
            detail="Decision must be HIRE or REJECT.",
        )

    if application.status not in {
        "INTERVIEWING",
        "OFFERED",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Hiring decision can only be made for "
                "INTERVIEWING or OFFERED applications."
            ),
        )

    previous_status = application.status

    if decision == "HIRE":
        completed_interview = get_latest_completed_interview(
            db,
            application.id,
        )

        if not completed_interview:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate must have a completed interview "
                    "before being hired."
                ),
            )

        application = mark_application_hired(
            db,
            application,
        )

        return HiringDecisionResponse(
            application_id=application.id,
            previous_status=previous_status,
            new_status=application.status,
            decision="HIRE",
            message="Candidate has been marked as hired.",
        )

    application = mark_application_rejected(
        db,
        application,
    )

    return HiringDecisionResponse(
        application_id=application.id,
        previous_status=previous_status,
        new_status=application.status,
        decision="REJECT",
        message="Candidate has been rejected.",
    )