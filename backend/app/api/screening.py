from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_company

from app.models.application import Application
from app.models.company import Company
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.user import User

from app.schemas.screening import ScreeningResponse

from app.services.screening_service import (
    screen_application,
)


router = APIRouter(
    prefix="/screening",
    tags=["AI Screening"],
)


# =========================================================
# 1. RUN AI SCREENING
# =========================================================

@router.post(
    "/applications/{application_id}",
    response_model=ScreeningResponse,
)
def screen_candidate_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------
    # 1. Get application
    # -----------------------------------------

    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.company_id == current_company.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # -----------------------------------------
    # 2. Run AI screening
    # -----------------------------------------

    try:
        result = screen_application(
            db=db,
            application_id=application_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"AI screening failed: {str(e)}",
        )

    return result


# =========================================================
# 2. GET AI SCREENING RESULT
# =========================================================

@router.get(
    "/applications/{application_id}",
)
def get_screening_result(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------
    # 1. Get application
    # -----------------------------------------

    application = (
        db.query(Application)
        .join(
            Job,
            Job.id == Application.job_id,
        )
        .filter(
            Application.id == application_id,
            Job.company_id == current_company.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # -----------------------------------------
    # 2. Get latest match result
    # -----------------------------------------

    match_result = (
        db.query(MatchResult)
        .filter(
            MatchResult.application_id == application.id
        )
        .order_by(
            MatchResult.created_at.desc()
        )
        .first()
    )

    if not match_result:
        raise HTTPException(
            status_code=404,
            detail="AI screening result not found.",
        )

    # -----------------------------------------
    # 3. Return screening result
    # -----------------------------------------

    return {
        "application_id": str(application.id),
        "job_id": str(application.job_id),
        "candidate_id": str(application.candidate_id),
        "status": application.status,
        "match_result": {
            "id": str(match_result.id),

            "overall_score": (
                float(match_result.overall_score)
                if match_result.overall_score is not None
                else None
            ),

            "skill_score": (
                float(match_result.skill_score)
                if match_result.skill_score is not None
                else None
            ),

            "experience_score": (
                float(match_result.experience_score)
                if match_result.experience_score is not None
                else None
            ),

            "education_score": (
                float(match_result.education_score)
                if match_result.education_score is not None
                else None
            ),

            "keyword_score": (
                float(match_result.keyword_score)
                if match_result.keyword_score is not None
                else None
            ),

            "classification": match_result.classification,

            "missing_skills": match_result.missing_skills,

            "explanation": match_result.explanation,
        },
    }