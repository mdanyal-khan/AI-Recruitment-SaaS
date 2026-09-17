from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_company

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.user import User

from app.schemas.hr_application import (
    HRApplicationDetail,
    HRApplicationListItem,
)

from app.services.hr_application_service import (
    get_job_applications,
    get_company_applications,
    get_candidate_user,
    get_application_resume,
    get_latest_match_result,
)


router = APIRouter(
    prefix="/hr/applications",
    tags=["HR Applications"],
)


# =========================================================
# 0. GET ALL APPLICATIONS FOR COMPANY (CANDIDATE POOL)
# =========================================================

@router.get(
    "",
    response_model=list[HRApplicationListItem],
)
def get_all_company_applications_for_hr(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    applications = get_company_applications(
        db=db,
        company_id=current_company.id,
    )
    if status and status != "ALL":
        applications = [a for a in applications if a.status == status]

    results = []
    for application in applications:
        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == application.candidate_id)
            .first()
        )
        if not candidate:
            continue

        candidate_user = get_candidate_user(
            db=db,
            candidate=candidate,
        )

        match_result = get_latest_match_result(
            db=db,
            application_id=application.id,
        )

        job = (
            db.query(Job)
            .filter(Job.id == application.job_id)
            .first()
        )

        results.append(
            HRApplicationListItem(
                application_id=application.id,
                candidate_id=candidate.id,
                candidate_name=(
                    f"{candidate_user.first_name or ''} {candidate_user.last_name or ''}".strip()
                    if candidate_user else None
                ),
                candidate_email=candidate_user.email if candidate_user else None,
                job_id=application.job_id,
                job_title=job.title if job else "Unknown",
                resume_id=application.resume_id,
                application_status=application.status,
                match_score=(
                    float(match_result.overall_score)
                    if match_result and match_result.overall_score is not None
                    else None
                ),
                classification=(
                    match_result.classification
                    if match_result
                    else None
                ),
                applied_at=application.applied_at,
            )
        )
    return results


# =========================================================
# 1. GET APPLICATIONS FOR A JOB
# =========================================================

@router.get(
    "/jobs/{job_id}",
    response_model=list[HRApplicationListItem],
)
def get_job_applications_for_hr(
    job_id: UUID,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------
    # 1. Get job and applications
    # -----------------------------------------

    job, applications = get_job_applications(
        db=db,
        job_id=job_id,
        company_id=current_company.id,
    )

    # -----------------------------------------
    # 2. Check job
    # -----------------------------------------

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # -----------------------------------------
    # 3. Filter by application status
    # -----------------------------------------

    if status:
        allowed_statuses = {
            "APPLIED",
            "SHORTLISTED",
            "INTERVIEWING",
            "OFFERED",
            "HIRED",
            "REJECTED",
            "WITHDRAWN",
        }

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid application status.",
            )

        applications = [
            application
            for application in applications
            if application.status == status
        ]

    # -----------------------------------------
    # 4. Build response
    # -----------------------------------------

    results = []

    for application in applications:

        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == application.candidate_id
            )
            .first()
        )

        if not candidate:
            continue

        candidate_user = get_candidate_user(
            db=db,
            candidate=candidate,
        )

        match_result = get_latest_match_result(
            db=db,
            application_id=application.id,
        )

        results.append(
            HRApplicationListItem(
                application_id=application.id,

                candidate_id=candidate.id,

                candidate_name=(
                    f"{candidate_user.first_name or ''} "
                    f"{candidate_user.last_name or ''}"
                ).strip()
                if candidate_user
                else None,

                candidate_email=(
                    candidate_user.email
                    if candidate_user
                    else None
                ),

                job_id=job.id,

                job_title=job.title,

                resume_id=application.resume_id,

                application_status=application.status,

                match_score=(
                    float(match_result.overall_score)
                    if match_result
                    and match_result.overall_score is not None
                    else None
                ),

                classification=(
                    match_result.classification
                    if match_result
                    else None
                ),

                applied_at=application.applied_at,
            )
        )

    return results


# =========================================================
# 2. GET SINGLE HR APPLICATION DETAIL
# =========================================================

@router.get(
    "/{application_id}",
    response_model=HRApplicationDetail,
)
def get_hr_application_detail(
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
    # 2. Get candidate
    # -----------------------------------------

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == application.candidate_id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    # -----------------------------------------
    # 3. Get candidate user
    # -----------------------------------------

    candidate_user = get_candidate_user(
        db=db,
        candidate=candidate,
    )

    # -----------------------------------------
    # 4. Get resume
    # -----------------------------------------

    resume = get_application_resume(
        db=db,
        application=application,
    )

    # -----------------------------------------
    # 5. Get latest match result
    # -----------------------------------------

    match_result = get_latest_match_result(
        db=db,
        application_id=application.id,
    )

    job = (
        db.query(Job)
        .filter(Job.id == application.job_id)
        .first()
    )

    # -----------------------------------------
    # 6. Return application details
    # -----------------------------------------

    return HRApplicationDetail(
        application_id=application.id,

        candidate_id=candidate.id,

        candidate_name=(
            f"{candidate_user.first_name or ''} "
            f"{candidate_user.last_name or ''}"
        ).strip()
        if candidate_user
        else None,

        candidate_email=(
            candidate_user.email
            if candidate_user
            else None
        ),

        job_id=application.job_id,

        job_title=(
            job.title
            if job
            else "Unknown"
        ),

        resume_id=application.resume_id,

        resume_file_name=(
            resume.file_name
            if resume
            else None
        ),

        resume_file_url=(
            resume.file_url
            if resume
            else None
        ),

        application_status=application.status,

        applied_at=application.applied_at,

        match_score=(
            float(match_result.overall_score)
            if match_result
            and match_result.overall_score is not None
            else None
        ),

        classification=(
            match_result.classification
            if match_result
            else None
        ),

        skill_score=(
            float(match_result.skill_score)
            if match_result
            and match_result.skill_score is not None
            else None
        ),

        experience_score=(
            float(match_result.experience_score)
            if match_result
            and match_result.experience_score is not None
            else None
        ),

        education_score=(
            float(match_result.education_score)
            if match_result
            and match_result.education_score is not None
            else None
        ),

        keyword_score=(
            float(match_result.keyword_score)
            if match_result
            and match_result.keyword_score is not None
            else None
        ),

        missing_skills=(
            match_result.missing_skills
            if match_result
            and match_result.missing_skills
            else []
        ),

        explanation=(
            match_result.explanation
            if match_result
            else None
        ),
    )