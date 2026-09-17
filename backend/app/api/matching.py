from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_company

from app.models.ai_analysis import AIAnalysis
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User

from app.services.matching_service import (
    match_candidate_to_job,
    save_match_result,
)


router = APIRouter(
    prefix="/matching",
    tags=["Matching"],
)


@router.post(
    "/jobs/{job_id}/candidates/{candidate_id}",
)
def match_candidate(
    job_id: UUID,
    candidate_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Match a candidate against a job using AI.
    """

    # -----------------------------------
    # 1. Find the job
    # -----------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # -----------------------------------
    # 2. Find the candidate
    # -----------------------------------

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    # -----------------------------------
    # 2b. Verify candidate applied to company or is self
    # -----------------------------------
    has_application = (
        db.query(Application)
        .join(Job, Job.id == Application.job_id)
        .filter(
            Job.company_id == current_company.id,
            Application.candidate_id == candidate_id,
        )
        .first()
    )

    if not has_application and current_user.id != candidate.user_id:
        raise HTTPException(
            status_code=403,
            detail="Candidate has not applied to any job openings at this company.",
        )

    # -----------------------------------
    # 3. Find candidate's primary resume
    # -----------------------------------

    resume = (
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

    if not resume:
        raise HTTPException(
            status_code=400,
            detail="Candidate does not have a primary resume.",
        )

    # -----------------------------------
    # 4. Get latest CV analysis
    # -----------------------------------

    cv_analysis = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.entity_type == "RESUME",
            AIAnalysis.entity_id == resume.id,
            AIAnalysis.analysis_type == "CV_ANALYSIS",
        )
        .order_by(
            AIAnalysis.created_at.desc()
        )
        .first()
    )

    if not cv_analysis:
        raise HTTPException(
            status_code=400,
            detail=(
                "Candidate CV has not been analyzed by AI yet. "
                "Please upload and analyze a resume first."
            ),
        )

    # -----------------------------------
    # 5. Get latest Job analysis
    # -----------------------------------

    job_analysis = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.entity_type == "JOB",
            AIAnalysis.entity_id == job_id,
            AIAnalysis.analysis_type == "JOB_ANALYSIS",
        )
        .order_by(
            AIAnalysis.created_at.desc()
        )
        .first()
    )

    if not job_analysis:
        raise HTTPException(
            status_code=400,
            detail=(
                "Job has not been analyzed by AI yet. "
                "Please analyze the job first."
            ),
        )

    # -----------------------------------
    # 6. Run AI matching
    # -----------------------------------

    try:
        match_result = match_candidate_to_job(
            cv_analysis=cv_analysis.result_json,
            job_analysis=job_analysis.result_json,
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
        raise HTTPException(
            status_code=500,
            detail=f"Matching failed: {str(e)}",
        )

    # -----------------------------------
    # 7. Save match result
    # -----------------------------------

    try:
        saved_match = save_match_result(
            db=db,
            job_id=job_id,
            candidate_id=candidate_id,
            match_result=match_result,
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save match result: {str(e)}"
            ),
        )

    # -----------------------------------
    # 8. Return result
    # -----------------------------------

    return {
        "message": "Candidate matched successfully",
        "match_id": str(saved_match.id),
        "job_id": str(saved_match.job_id),
        "candidate_id": str(saved_match.candidate_id),
        "overall_score": float(
            saved_match.overall_score
        ),
        "classification": saved_match.classification,
        "missing_skills": saved_match.missing_skills,
        "explanation": saved_match.explanation,
    }