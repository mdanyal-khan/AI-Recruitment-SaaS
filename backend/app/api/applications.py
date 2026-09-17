from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import get_current_company

from app.models.ai_analysis import AIAnalysis
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.user import User

from app.services.application_service import (
    create_application,
    get_application_for_company,
    get_candidate_by_user_id,
    get_existing_application,
    get_job,
    get_job_applications,
    get_primary_resume,
    update_application_status,
)

from app.services.email_templates import (
    rejection_email,
    shortlist_email,
)

from app.services.notification_service import (
    create_notification,
    send_notification_email,
)

from app.services.matching_service import (
    match_candidate_to_job,
    save_match_result,
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


# ============================================================
# APPLY TO JOB
# ============================================================

@router.post("/jobs/{job_id}")
def apply_to_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Candidate applies to a published job.

    Workflow:

    1. Get candidate
    2. Get job
    3. Verify job is published
    4. Check duplicate application
    5. Get primary resume
    6. Get CV analysis
    7. Get job analysis
    8. Create application
    9. Match candidate against job
    10. Save match result
    """

    # --------------------------------------------------------
    # Get candidate
    # --------------------------------------------------------

    candidate = get_candidate_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    # --------------------------------------------------------
    # Get job
    # --------------------------------------------------------

    job = get_job(
        db=db,
        job_id=job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Check job status
    # --------------------------------------------------------

    if job.status != "PUBLISHED":
        raise HTTPException(
            status_code=400,
            detail=(
                "This job is not currently "
                "accepting applications."
            ),
        )

    # --------------------------------------------------------
    # Check duplicate application
    # --------------------------------------------------------

    existing_application = get_existing_application(
        db=db,
        job_id=job_id,
        candidate_id=candidate.id,
    )

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You have already applied to this job.",
        )

    # --------------------------------------------------------
    # Get primary resume
    # --------------------------------------------------------

    resume = get_primary_resume(
        db=db,
        candidate_id=candidate.id,
    )

    if not resume:
        raise HTTPException(
            status_code=400,
            detail=(
                "You must upload a primary resume "
                "before applying."
            ),
        )

    # --------------------------------------------------------
    # Get CV analysis
    # --------------------------------------------------------

    cv_analysis_record = (
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

    if not cv_analysis_record:
        raise HTTPException(
            status_code=400,
            detail="Resume has not been analyzed yet.",
        )

    cv_analysis = cv_analysis_record.result_json

    # --------------------------------------------------------
    # Get job analysis
    # --------------------------------------------------------

    job_analysis_record = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.entity_type == "JOB",
            AIAnalysis.entity_id == job.id,
            AIAnalysis.analysis_type == "JOB_ANALYSIS",
        )
        .order_by(
            AIAnalysis.created_at.desc()
        )
        .first()
    )

    if not job_analysis_record:
        raise HTTPException(
            status_code=400,
            detail="Job has not been analyzed yet.",
        )

    job_analysis = job_analysis_record.result_json

    # --------------------------------------------------------
    # Create application
    # --------------------------------------------------------

    application = create_application(
        db=db,
        job_id=job.id,
        candidate_id=candidate.id,
        resume_id=resume.id,
    )

    # --------------------------------------------------------
    # Match candidate against job
    # --------------------------------------------------------

    match_result = match_candidate_to_job(
        cv_analysis=cv_analysis,
        job_analysis=job_analysis,
    )

    # --------------------------------------------------------
    # Save match result
    # --------------------------------------------------------

    saved_match = save_match_result(
        db=db,
        job_id=job.id,
        candidate_id=candidate.id,
        application_id=application.id,
        match_result=match_result,
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Application submitted successfully.",
        "application": {
            "id": str(application.id),
            "job_id": str(application.job_id),
            "candidate_id": str(application.candidate_id),
            "resume_id": str(application.resume_id),
            "status": application.status,
            "applied_at": application.applied_at,
        },
        "match": {
            "id": str(saved_match.id),
            "overall_score": saved_match.overall_score,
            "classification": saved_match.classification,
            "explanation": saved_match.explanation,
            "missing_skills": saved_match.missing_skills,
        },
    }


# ============================================================
# GET JOB APPLICANTS
# ============================================================

@router.get("/jobs/{job_id}")
def get_applicants(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    HR gets all applicants for a job.
    """

    # --------------------------------------------------------
    # Verify job belongs to company
    # --------------------------------------------------------

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
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Get applicants
    # --------------------------------------------------------

    applications = get_job_applications(
        db=db,
        job_id=job_id,
        company_id=current_company.id,
    )

    results = []

    for application, candidate, user, match_result in applications:

        results.append(
            {
                "application_id": str(
                    application.id
                ),
                "candidate_id": str(
                    candidate.id
                ),
                "candidate_name": (
                    f"{user.first_name or ''} "
                    f"{user.last_name or ''}"
                ).strip(),
                "candidate_email": user.email,
                "status": application.status,
                "applied_at": application.applied_at,
                "match": (
                    {
                        "id": str(
                            match_result.id
                        ),
                        "overall_score": (
                            match_result.overall_score
                        ),
                        "skill_score": (
                            match_result.skill_score
                        ),
                        "experience_score": (
                            match_result.experience_score
                        ),
                        "education_score": (
                            match_result.education_score
                        ),
                        "keyword_score": (
                            match_result.keyword_score
                        ),
                        "classification": (
                            match_result.classification
                        ),
                        "explanation": (
                            match_result.explanation
                        ),
                        "missing_skills": (
                            match_result.missing_skills
                        ),
                    }
                    if match_result
                    else None
                ),
            }
        )

    return {
        "job_id": str(job.id),
        "job_title": job.title,
        "total_applicants": len(results),
        "applicants": results,
    }


# ============================================================
# GET MY APPLICATIONS
# ============================================================

@router.get("/my")
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Candidate gets all of their own job applications.
    """

    # --------------------------------------------------------
    # Get candidate profile
    # --------------------------------------------------------

    candidate = get_candidate_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    # --------------------------------------------------------
    # Get applications
    # --------------------------------------------------------

    applications = (
        db.query(Application)
        .filter(
            Application.candidate_id == candidate.id
        )
        .order_by(
            Application.applied_at.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "total": len(applications),
        "applications": [
            {
                "id": str(application.id),
                "job_id": str(application.job_id),
                "candidate_id": str(
                    application.candidate_id
                ),
                "resume_id": (
                    str(application.resume_id)
                    if application.resume_id
                    else None
                ),
                "status": application.status,
                "applied_at": application.applied_at,
                "updated_at": application.updated_at,
            }
            for application in applications
        ],
    }


# ============================================================
# GET MY APPLICATION DETAILS
# ============================================================

@router.get("/my/{application_id}")
def get_my_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Candidate gets one of their own applications.
    """

    # --------------------------------------------------------
    # Get candidate profile
    # --------------------------------------------------------

    candidate = get_candidate_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    # --------------------------------------------------------
    # Get application
    # --------------------------------------------------------

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.candidate_id == candidate.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "id": str(application.id),
        "job_id": str(application.job_id),
        "candidate_id": str(application.candidate_id),
        "resume_id": (
            str(application.resume_id)
            if application.resume_id
            else None
        ),
        "status": application.status,
        "applied_at": application.applied_at,
        "updated_at": application.updated_at,
    }


# ============================================================
# GET APPLICATION DETAILS
# ============================================================

@router.get("/{application_id}")
def get_application_details(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    HR gets detailed information about an application.
    """

    application = get_application_for_company(
        db=db,
        application_id=application_id,
        company_id=current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # --------------------------------------------------------
    # Candidate
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Candidate user
    # --------------------------------------------------------

    candidate_user = (
        db.query(User)
        .filter(
            User.id == candidate.user_id
        )
        .first()
    )

    if not candidate_user:
        raise HTTPException(
            status_code=404,
            detail="Candidate user not found.",
        )

    # --------------------------------------------------------
    # Job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Match result
    # --------------------------------------------------------

    match_result = (
        db.query(MatchResult)
        .filter(
            MatchResult.application_id
            == application.id
        )
        .order_by(
            MatchResult.created_at.desc()
        )
        .first()
    )

    return {
        "application": {
            "id": str(application.id),
            "job_id": str(application.job_id),
            "candidate_id": str(
                application.candidate_id
            ),
            "resume_id": (
                str(application.resume_id)
                if application.resume_id
                else None
            ),
            "status": application.status,
            "applied_at": application.applied_at,
        },
        "candidate": {
            "id": str(candidate.id),
            "first_name": candidate_user.first_name,
            "last_name": candidate_user.last_name,
            "email": candidate_user.email,
            "headline": candidate.headline,
            "summary": candidate.summary,
            "location": candidate.location,
            "phone": candidate.phone,
            "linkedin_url": candidate.linkedin_url,
            "github_url": candidate.github_url,
            "portfolio_url": candidate.portfolio_url,
            "years_experience": (
                candidate.years_experience
            ),
        },
        "job": {
            "id": str(job.id),
            "title": job.title,
            "company_id": str(job.company_id),
            "status": job.status,
        },
        "match": (
            {
                "id": str(match_result.id),
                "overall_score": (
                    match_result.overall_score
                ),
                "skill_score": (
                    match_result.skill_score
                ),
                "experience_score": (
                    match_result.experience_score
                ),
                "education_score": (
                    match_result.education_score
                ),
                "keyword_score": (
                    match_result.keyword_score
                ),
                "classification": (
                    match_result.classification
                ),
                "explanation": (
                    match_result.explanation
                ),
                "missing_skills": (
                    match_result.missing_skills
                ),
                "created_at": (
                    match_result.created_at
                ),
            }
            if match_result
            else None
        ),
    }


# ============================================================
# SHORTLIST APPLICATION
# ============================================================

@router.patch("/{application_id}/shortlist")
def shortlist_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    HR shortlists a candidate.

    Workflow:

    1. Verify application belongs to company
    2. Validate current application status
    3. Update application to SHORTLISTED
    4. Get candidate
    5. Get candidate user
    6. Get job
    7. Generate shortlist email
    8. Create EMAIL notification
    9. Send email
    """

    # --------------------------------------------------------
    # Get application
    # --------------------------------------------------------

    application = get_application_for_company(
        db=db,
        application_id=application_id,
        company_id=current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if application.status in [
        "REJECTED",
        "WITHDRAWN",
        "HIRED",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Application cannot be shortlisted "
                f"because its current status is "
                f"{application.status}."
            ),
        )

    # --------------------------------------------------------
    # Update application status
    # --------------------------------------------------------

    application = update_application_status(
        db=db,
        application=application,
        status="SHORTLISTED",
    )

    # --------------------------------------------------------
    # Get candidate
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get candidate user
    # --------------------------------------------------------

    candidate_user = (
        db.query(User)
        .filter(
            User.id == candidate.user_id
        )
        .first()
    )

    if not candidate_user:
        raise HTTPException(
            status_code=404,
            detail="Candidate user not found.",
        )

    # --------------------------------------------------------
    # Get job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Candidate name
    # --------------------------------------------------------

    candidate_name = (
        candidate_user.first_name
        or "Candidate"
    )

    # --------------------------------------------------------
    # Generate shortlist email
    # --------------------------------------------------------

    email_html = shortlist_email(
        candidate_name=candidate_name,
        job_title=job.title,
    )

    # --------------------------------------------------------
    # Create notification
    # --------------------------------------------------------

    notification = create_notification(
        db=db,
        user_id=candidate_user.id,
        notification_type="APPLICATION_UPDATE",
        channel="EMAIL",
        subject=(
            f"Application Shortlisted — "
            f"{job.title}"
        ),
        message=email_html,
    )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:
        notification = send_notification_email(
            db=db,
            notification=notification,
            recipient_email=candidate_user.email,
        )

    except RuntimeError:
        # The application is already shortlisted.
        # Email failure should not undo the status update.
        pass

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Candidate shortlisted successfully."
        ),
        "application_id": str(
            application.id
        ),
        "status": application.status,
        "notification": {
            "type": notification.type,
            "channel": notification.channel,
            "status": notification.status,
        },
    }


# ============================================================
# REJECT APPLICATION
# ============================================================

@router.patch("/{application_id}/reject")
def reject_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    HR rejects a candidate application.

    Workflow:

    1. Verify application belongs to company
    2. Validate current application status
    3. Update application to REJECTED
    4. Get candidate
    5. Get candidate user
    6. Get job
    7. Generate rejection email
    8. Create EMAIL notification
    9. Send email
    """

    # --------------------------------------------------------
    # Get application
    # --------------------------------------------------------

    application = get_application_for_company(
        db=db,
        application_id=application_id,
        company_id=current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if application.status in [
        "REJECTED",
        "WITHDRAWN",
        "HIRED",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Application cannot be rejected "
                f"because its current status is "
                f"{application.status}."
            ),
        )

    # --------------------------------------------------------
    # Update application status
    # --------------------------------------------------------

    application = update_application_status(
        db=db,
        application=application,
        status="REJECTED",
    )

    # --------------------------------------------------------
    # Get candidate
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get candidate user
    # --------------------------------------------------------

    candidate_user = (
        db.query(User)
        .filter(
            User.id == candidate.user_id
        )
        .first()
    )

    if not candidate_user:
        raise HTTPException(
            status_code=404,
            detail="Candidate user not found.",
        )

    # --------------------------------------------------------
    # Get job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # --------------------------------------------------------
    # Generate rejection email
    # --------------------------------------------------------

    candidate_name = (
        candidate_user.first_name
        or "Candidate"
    )

    email_html = rejection_email(
        candidate_name=candidate_name,
        job_title=job.title,
    )

    # --------------------------------------------------------
    # Create notification
    # --------------------------------------------------------

    notification = create_notification(
        db=db,
        user_id=candidate_user.id,
        notification_type="REJECTION",
        channel="EMAIL",
        subject=(
            f"Application Update — "
            f"{job.title}"
        ),
        message=email_html,
    )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:
        notification = send_notification_email(
            db=db,
            notification=notification,
            recipient_email=candidate_user.email,
        )

    except RuntimeError:
        # Application remains rejected even if email fails.
        pass

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Application rejected successfully."
        ),
        "application_id": str(
            application.id
        ),
        "status": application.status,
        "notification": {
            "type": notification.type,
            "channel": notification.channel,
            "status": notification.status,
        },
    }