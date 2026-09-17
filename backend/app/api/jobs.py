from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_company

from app.models.company import Company
from app.models.job import Job
from app.models.user import User

from app.schemas.job import JobCreate, JobResponse, JobUpdate

from app.services.ai_analysis_service import (
    analyze_job_text,
    save_job_analysis,
)


router = APIRouter(
    prefix="/companies",
    tags=["Jobs"]
)


# =========================
# CREATE JOB
# =========================

@router.post(
    "/{company_id}/jobs",
    response_model=JobResponse,
    status_code=201,
)
def create_job(
    company_id: UUID,
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):

    # Verify company access
    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company",
        )

    # =========================
    # CREATE JOB DATABASE RECORD
    # =========================

    job = Job(
        company_id=current_company.id,
        created_by=current_user.id,

        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        employment_type=job_data.employment_type,

        experience_min=job_data.experience_min,
        experience_max=job_data.experience_max,

        education_level=job_data.education_level,

        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,

        deadline=job_data.deadline,

        # New jobs start as DRAFT
        status="DRAFT",
    )

    db.add(job)
    db.flush()

    # =========================
    # BUILD AI INPUT
    # =========================

    job_text = f"""
Job Title:
{job.title}

Description:
{job.description or ""}

Location:
{job.location or ""}

Employment Type:
{job.employment_type or ""}

Minimum Experience:
{job.experience_min if job.experience_min is not None else ""}

Maximum Experience:
{job.experience_max if job.experience_max is not None else ""}

Education:
{job.education_level or ""}

Responsibilities and Requirements:
{job.description or ""}
"""

    # =========================
    # ANALYZE JOB WITH AI
    # =========================

    try:
        analysis_result = analyze_job_text(
            job_text
        )
    except Exception as e:
        # Fallback to structured analysis so job creation does not fail on external AI timeouts/errors
        analysis_result = {
            "job_title": job.title,
            "summary": job.description or "",
            "required_skills": [],
            "preferred_skills": [],
            "required_experience_years": float(job.experience_min or 0),
            "preferred_experience_years": float(job.experience_max or 0),
            "education_requirements": [job.education_level] if job.education_level else [],
            "responsibilities": [job.description] if job.description else [],
            "employment_type": job.employment_type or "FULL_TIME",
            "location": job.location or "Remote",
            "certifications": [],
            "languages": [],
        }

    # =========================
    # SAVE AI ANALYSIS
    # =========================

    try:
        save_job_analysis(
            db=db,
            job_id=job.id,
            analysis_result=analysis_result,
        )
    except Exception as e:
        pass

    # =========================
    # COMMIT JOB + AI ANALYSIS
    # =========================

    try:

        db.commit()
        db.refresh(job)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save job: "
                f"{str(e)}"
            ),
        )

    return job


# =========================
# GET ALL JOBS
# =========================

@router.get(
    "/{company_id}/jobs",
    response_model=list[JobResponse]
)
def get_jobs(
    company_id: UUID,
    status: str | None = Query(
        default=None,
        pattern="^(DRAFT|PUBLISHED|CLOSED|ARCHIVED)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    # Verify company access
    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    query = (
        db.query(Job)
        .filter(
            Job.company_id == current_company.id
        )
    )

    if status:
        query = query.filter(
            Job.status == status
        )

    jobs = (
        query
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return jobs


# =========================
# GET SINGLE JOB
# =========================

@router.get(
    "/{company_id}/jobs/{job_id}",
    response_model=JobResponse
)
def get_job(
    company_id: UUID,
    job_id: UUID,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    # Verify company access
    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# =========================
# UPDATE JOB
# =========================

@router.put(
    "/{company_id}/jobs/{job_id}",
    response_model=JobResponse
)
def update_job(
    company_id: UUID,
    job_id: UUID,
    job_data: JobUpdate,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    # Verify company access
    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


# =========================
# PUBLISH JOB
# =========================

@router.patch(
    "/{company_id}/jobs/{job_id}/publish",
    response_model=JobResponse
)
def publish_job(
    company_id: UUID,
    job_id: UUID,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.status != "DRAFT":
        raise HTTPException(
            status_code=400,
            detail="Only draft jobs can be published"
        )

    job.status = "PUBLISHED"

    db.commit()
    db.refresh(job)

    return job


# =========================
# CLOSE JOB
# =========================

@router.patch(
    "/{company_id}/jobs/{job_id}/close",
    response_model=JobResponse
)
def close_job(
    company_id: UUID,
    job_id: UUID,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.status != "PUBLISHED":
        raise HTTPException(
            status_code=400,
            detail="Only published jobs can be closed"
        )

    job.status = "CLOSED"

    db.commit()
    db.refresh(job)

    return job


# =========================
# ARCHIVE JOB
# =========================

@router.patch(
    "/{company_id}/jobs/{job_id}/archive",
    response_model=JobResponse
)
def archive_job(
    company_id: UUID,
    job_id: UUID,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):

    if company_id != current_company.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.company_id == current_company.id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.status != "CLOSED":
        raise HTTPException(
            status_code=400,
            detail="Only closed jobs can be archived"
        )

    job.status = "ARCHIVED"

    db.commit()
    db.refresh(job)

    return job


# ============================================================
# PUBLIC / CANDIDATE PUBLISHED JOBS ROUTER
# ============================================================

public_router = APIRouter(
    prefix="/jobs",
    tags=["Candidate Jobs"]
)


@public_router.get(
    "",
    response_model=list[JobResponse],
)
def get_all_published_jobs(
    search: str | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all active PUBLISHED jobs across all companies for candidates and job seekers.
    """
    query = db.query(Job).filter(Job.status == "PUBLISHED")

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(Job.title.ilike(search_fmt) | Job.description.ilike(search_fmt))

    if location:
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    if employment_type and employment_type != "ALL":
        query = query.filter(Job.employment_type == employment_type)

    jobs = (
        query
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return jobs


@public_router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_published_job_detail(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single published job opening for candidate view.
    """
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.status == "PUBLISHED"
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Published job opening not found"
        )

    return job

