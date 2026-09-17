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

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.company import Company
from app.models.interview import Interview
from app.models.job import Job
from app.models.user import User

from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
)

from app.schemas.interview_feedback import (
    InterviewFeedbackCreate,
)

from app.services.email_templates import (
    interview_invitation_email,
)

from app.services.notification_service import (
    create_notification,
    send_notification_email,
)

from app.services.interview_service import (
    create_feedback,
    create_interview,
    get_application_for_company,
    get_interview_for_company,
    get_active_interview_for_application,
    get_candidate_for_application,
    get_user_for_candidate,
)

from app.services.interview_validation_service import (
    validate_interview_time,
    check_time_conflict,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


# =========================================================
# 0. LIST COMPANY INTERVIEWS (HR)
# =========================================================

@router.get(
    "",
    response_model=list[InterviewResponse],
)
def list_company_interviews(
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    interviews = (
        db.query(Interview)
        .join(Application, Application.id == Interview.application_id)
        .join(Job, Job.id == Application.job_id)
        .filter(Job.company_id == current_company.id)
        .order_by(Interview.start_time.desc())
        .all()
    )
    return interviews


# =========================================================
# 1. SCHEDULE INTERVIEW
# =========================================================

@router.post(
    "",
    response_model=InterviewResponse,
)
def schedule_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find application belonging to current company
    # -----------------------------------------------------

    application = get_application_for_company(
        db=db,
        application_id=interview_data.application_id,
        company_id=current_company.id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    # -----------------------------------------------------
    # 2. Only shortlisted candidates can be interviewed
    # -----------------------------------------------------

    if application.status not in [
        "SHORTLISTED",
        "INTERVIEWING",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only shortlisted candidates can be "
                "scheduled for an interview."
            ),
        )

    # -----------------------------------------------------
    # 3. Check existing active interview
    # -----------------------------------------------------

    active_interview = get_active_interview_for_application(
        db=db,
        application_id=application.id,
    )

    if active_interview:
        raise HTTPException(
            status_code=400,
            detail=(
                "This application already has an active "
                "interview."
            ),
        )

    # -----------------------------------------------------
    # 4. Validate interview time
    # -----------------------------------------------------

    try:
        validate_interview_time(
            start_time=interview_data.start_time,
            end_time=interview_data.end_time,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    # -----------------------------------------------------
    # 5. Check HR time conflict
    # -----------------------------------------------------

    conflict = check_time_conflict(
        db=db,
        start_time=interview_data.start_time,
        end_time=interview_data.end_time,
        scheduled_by=current_user.id,
    )

    if conflict:
        raise HTTPException(
            status_code=409,
            detail=(
                "You already have another interview "
                "scheduled during this time."
            ),
        )

    # -----------------------------------------------------
    # 6. Create interview
    # -----------------------------------------------------

    try:
        interview = create_interview(
            db=db,
            application=application,
            scheduled_by=current_user.id,
            start_time=interview_data.start_time,
            end_time=interview_data.end_time,
            timezone=interview_data.timezone,
            mode=interview_data.mode,
            meeting_url=interview_data.meeting_url,
            location=interview_data.location,
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create interview: {str(e)}",
        )

    # -----------------------------------------------------
    # 7. Get candidate
    # -----------------------------------------------------

    candidate = get_candidate_for_application(
        db=db,
        application=application,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    # -----------------------------------------------------
    # 8. Get candidate user
    # -----------------------------------------------------

    candidate_user = get_user_for_candidate(
        db=db,
        candidate=candidate,
    )

    if not candidate_user:
        raise HTTPException(
            status_code=404,
            detail="Candidate user not found.",
        )

    # -----------------------------------------------------
    # 9. Get job
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 10. Create interview email
    # -----------------------------------------------------

    candidate_name = (
        candidate_user.first_name
        or "Candidate"
    )

    email_html = interview_invitation_email(
        candidate_name=candidate_name,
        job_title=job.title,
        start_time=str(interview.start_time),
        end_time=str(interview.end_time),
        timezone=interview.timezone or "UTC",
        mode=interview.mode,
        meeting_url=interview.meeting_url,
        location=interview.location,
    )

    # -----------------------------------------------------
    # 11. Create notification
    # -----------------------------------------------------

    notification = create_notification(
        db=db,
        user_id=candidate_user.id,
        notification_type="INTERVIEW_INVITATION",
        channel="EMAIL",
        subject=f"Interview Invitation — {job.title}",
        message=email_html,
    )

    # -----------------------------------------------------
    # 12. Send email
    # -----------------------------------------------------

    try:
        notification = send_notification_email(
            db=db,
            notification=notification,
            recipient_email=candidate_user.email,
        )

    except RuntimeError:
        # The interview has already been created.
        # Email failure should not delete the interview.
        pass

    # -----------------------------------------------------
    # 13. Return interview
    # -----------------------------------------------------

    return interview


# =========================================================
# 2. GET MY INTERVIEWS
# =========================================================

@router.get("/my")
def get_my_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find candidate profile
    # -----------------------------------------------------

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.user_id == current_user.id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    # -----------------------------------------------------
    # 2. Get candidate interviews
    # -----------------------------------------------------

    interviews = (
        db.query(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .filter(
            Application.candidate_id == candidate.id,
        )
        .order_by(
            Interview.start_time.asc()
        )
        .all()
    )

    # -----------------------------------------------------
    # 3. Return interviews
    # -----------------------------------------------------

    return {
        "total": len(interviews),
        "interviews": [
            {
                "id": str(interview.id),
                "application_id": str(
                    interview.application_id
                ),
                "start_time": interview.start_time,
                "end_time": interview.end_time,
                "timezone": interview.timezone,
                "mode": interview.mode,
                "meeting_url": interview.meeting_url,
                "location": interview.location,
                "status": interview.status,
            }
            for interview in interviews
        ],
    }


# =========================================================
# 3. CONFIRM INTERVIEW
# =========================================================

@router.patch("/{interview_id}/confirm")
def confirm_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find candidate profile
    # -----------------------------------------------------

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.user_id == current_user.id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found.",
        )

    # -----------------------------------------------------
    # 2. Find candidate's interview
    # -----------------------------------------------------

    interview = (
        db.query(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .filter(
            Interview.id == interview_id,
            Application.candidate_id == candidate.id,
        )
        .first()
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    # -----------------------------------------------------
    # 3. Only scheduled interviews can be confirmed
    # -----------------------------------------------------

    if interview.status != "SCHEDULED":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only scheduled interviews "
                "can be confirmed."
            ),
        )

    # -----------------------------------------------------
    # 4. Confirm interview
    # -----------------------------------------------------

    interview.status = "CONFIRMED"

    db.commit()
    db.refresh(interview)

    return {
        "message": "Interview confirmed.",
        "interview_id": str(interview.id),
        "status": interview.status,
    }


# =========================================================
# 4. CANCEL INTERVIEW
# =========================================================

@router.patch("/{interview_id}/cancel")
def cancel_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find interview belonging to company
    # -----------------------------------------------------

    interview = get_interview_for_company(
        db=db,
        interview_id=interview_id,
        company_id=current_company.id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    # -----------------------------------------------------
    # 2. Completed, cancelled and no-show interviews
    #    cannot be cancelled
    # -----------------------------------------------------

    if interview.status in [
        "COMPLETED",
        "CANCELLED",
        "NO_SHOW",
    ]:
        raise HTTPException(
            status_code=400,
            detail="This interview cannot be cancelled.",
        )

    # -----------------------------------------------------
    # 3. Cancel interview
    # -----------------------------------------------------

    interview.status = "CANCELLED"

    db.commit()
    db.refresh(interview)

    return {
        "message": "Interview cancelled successfully.",
        "interview_id": str(interview.id),
        "status": interview.status,
    }


# =========================================================
# 5. COMPLETE INTERVIEW
# =========================================================

@router.patch("/{interview_id}/complete")
def complete_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find interview belonging to company
    # -----------------------------------------------------

    interview = get_interview_for_company(
        db=db,
        interview_id=interview_id,
        company_id=current_company.id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    # -----------------------------------------------------
    # 2. Only scheduled or confirmed interviews
    #    can be completed
    # -----------------------------------------------------

    if interview.status not in [
        "SCHEDULED",
        "CONFIRMED",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only scheduled or confirmed "
                "interviews can be completed."
            ),
        )

    # -----------------------------------------------------
    # 3. Complete interview
    # -----------------------------------------------------

    interview.status = "COMPLETED"

    db.commit()
    db.refresh(interview)

    return {
        "message": "Interview completed.",
        "interview_id": str(interview.id),
        "status": interview.status,
    }


# =========================================================
# 6. MARK INTERVIEW AS NO-SHOW
# =========================================================

@router.patch("/{interview_id}/no-show")
def mark_interview_no_show(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find interview belonging to company
    # -----------------------------------------------------

    interview = get_interview_for_company(
        db=db,
        interview_id=interview_id,
        company_id=current_company.id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    # -----------------------------------------------------
    # 2. Only scheduled or confirmed interviews
    #    can be marked as no-show
    # -----------------------------------------------------

    if interview.status not in [
        "SCHEDULED",
        "CONFIRMED",
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only scheduled or confirmed interviews "
                "can be marked as no-show."
            ),
        )

    # -----------------------------------------------------
    # 3. Mark interview as no-show
    # -----------------------------------------------------

    interview.status = "NO_SHOW"

    db.commit()
    db.refresh(interview)

    return {
        "message": "Interview marked as no-show.",
        "interview_id": str(interview.id),
        "status": interview.status,
    }


# =========================================================
# 7. ADD INTERVIEW FEEDBACK
# =========================================================

@router.post("/{interview_id}/feedback")
def add_interview_feedback(
    interview_id: UUID,
    data: InterviewFeedbackCreate,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Find interview belonging to company
    # -----------------------------------------------------

    interview = get_interview_for_company(
        db=db,
        interview_id=interview_id,
        company_id=current_company.id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    # -----------------------------------------------------
    # 2. Interview must be completed
    # -----------------------------------------------------

    if interview.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=(
                "Feedback can only be added "
                "after the interview is completed."
            ),
        )

    # -----------------------------------------------------
    # 3. Create feedback
    # -----------------------------------------------------

    try:
        feedback = create_feedback(
            db=db,
            interview_id=interview.id,
            reviewer_id=current_user.id,
            rating=data.rating,
            technical_score=data.technical_score,
            communication_score=data.communication_score,
            culture_score=data.culture_score,
            comments=data.comments,
            recommendation=data.recommendation,
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save feedback: {str(e)}",
        )

    # -----------------------------------------------------
    # 4. Return feedback
    # -----------------------------------------------------

    return {
        "message": "Interview feedback saved successfully.",
        "feedback": {
            "id": str(feedback.id),
            "interview_id": str(feedback.interview_id),
            "reviewer_id": (
                str(feedback.reviewer_id)
                if feedback.reviewer_id
                else None
            ),
            "rating": (
                float(feedback.rating)
                if feedback.rating is not None
                else None
            ),
            "technical_score": (
                float(feedback.technical_score)
                if feedback.technical_score is not None
                else None
            ),
            "communication_score": (
                float(feedback.communication_score)
                if feedback.communication_score is not None
                else None
            ),
            "culture_score": (
                float(feedback.culture_score)
                if feedback.culture_score is not None
                else None
            ),
            "comments": feedback.comments,
            "recommendation": feedback.recommendation,
        },
    }


    # =========================================================
# 3. GET INTERVIEW DETAILS
# =========================================================

@router.get("/{interview_id}")
def get_interview_details(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    interview = get_interview_for_company(
        db=db,
        interview_id=interview_id,
        company_id=current_company.id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    return {
        "id": str(interview.id),
        "application_id": str(
            interview.application_id
        ),
        "scheduled_by": (
            str(interview.scheduled_by)
            if interview.scheduled_by
            else None
        ),
        "start_time": interview.start_time,
        "end_time": interview.end_time,
        "timezone": interview.timezone,
        "mode": interview.mode,
        "meeting_url": interview.meeting_url,
        "location": interview.location,
        "status": interview.status,
        "created_at": interview.created_at,
        "updated_at": interview.updated_at,
    }