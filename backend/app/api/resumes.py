import logging
from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.supabase import supabase

from app.dependencies.auth import get_current_user

from app.models.user import User
from app.models.candidate import Candidate
from app.models.resume import Resume

from app.schemas.resume import ResumeResponse

from app.services.resume_processor import process_resume

from app.services.ai_analysis_service import (
    analyze_cv_text,
    save_cv_analysis,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/candidates",
    tags=["Resumes"],
)


# =========================================================
# UPLOAD RESUME
# =========================================================

@router.post(
    "/resume",
    response_model=ResumeResponse,
    status_code=201,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =====================================================
    # 1. Find candidate profile
    # =====================================================

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
            detail="Candidate profile not found",
        )

    # =====================================================
    # 2. Check file type
    # =====================================================

    filename_lower = (file.filename or "").lower()
    allowed_extensions = {".pdf"}
    file_ext = Path(filename_lower).suffix

    content_type = (
        file.content_type or ""
    ).lower()

    allowed_types = {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }

    if file_ext not in allowed_extensions or (content_type and content_type not in allowed_types):
        raise HTTPException(
            status_code=400,
            detail="Only PDF format (.pdf) is supported by the resume analysis engine.",
        )

    # Database file_type value
    file_type = content_type or "application/pdf"

    # =====================================================
    # 3. Read uploaded file
    # =====================================================

    try:
        file_data = await file.read()
    except Exception:
        logger.exception("Failed to read uploaded resume file")
        raise HTTPException(
            status_code=400,
            detail="Failed to read uploaded file.",
        )

    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # =====================================================
    # 4. Check file size (10 MB max)
    # =====================================================

    MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB

    if len(file_data) > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume file is too large. Maximum size is 10 MB.",
        )

    # =====================================================
    # 5. Make filename safe
    # =====================================================

    original_filename = (
        file.filename or "resume.pdf"
    )

    clean_stem = "".join(c for c in Path(original_filename).stem if c.isalnum() or c in "-_") or "resume"
    safe_filename = f"{clean_stem}.pdf"

    # =====================================================
    # 6. Extract text from PDF
    # =====================================================

    try:

        extracted_text = process_resume(
            file_data
        )

    except (ValueError, RuntimeError) as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to process PDF: "
                f"{str(e)}"
            ),
        )

    if not extracted_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract readable text "
                "from this PDF."
            ),
        )

    logger.debug("Resume text extracted successfully, length=%d", len(extracted_text))

    # =====================================================
    # 7. Analyze CV with Groq AI
    # =====================================================

    try:

        analysis_result = analyze_cv_text(
            extracted_text
        )

        logger.info("AI CV analysis completed successfully.")

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
            detail=(
                "Failed to analyze CV with AI: "
                f"{str(e)}"
            ),
        )

    # =====================================================
    # 8. Find highest resume version
    # =====================================================

    highest_version = (
        db.query(
            func.max(Resume.version)
        )
        .filter(
            Resume.candidate_id == candidate.id
        )
        .scalar()
    )

    if highest_version is None:

        highest_version = 0

    new_version = (
        highest_version + 1
    )

    # =====================================================
    # 9. Create unique storage path
    # =====================================================

    file_path = (
        f"{candidate.id}/"
        f"v{new_version}_{safe_filename}"
    )

    logger.debug("Storage path: %s", file_path)

    # =====================================================
    # 10. Upload PDF to Supabase Storage
    # =====================================================

    try:

        storage_response = (
            supabase.storage
            .from_("resumes")
            .upload(
                file_path,
                file_data,
                file_options={
                    "content-type": "application/pdf",
                    "upsert": "false",
                },
            )
        )

        logger.debug("Storage upload response: %s", storage_response)

    except Exception as e:

        logger.error("Storage upload failed: %r", e)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to upload resume to "
                f"Supabase Storage: {str(e)}"
            ),
        )

    # =====================================================
    # 11. Remove primary flag from old resumes
    # =====================================================

    try:

        db.query(Resume).filter(
            Resume.candidate_id == candidate.id,
            Resume.is_primary.is_(True),
        ).update(
            {
                Resume.is_primary: False,
            },
            synchronize_session=False,
        )

        db.flush()

    except Exception as e:

        db.rollback()

        logger.error("Failed to update primary flag: %r", e)

        # Remove uploaded file because database
        # operation failed

        try:

            (
                supabase.storage
                .from_("resumes")
                .remove([file_path])
            )

        except Exception as storage_error:

            logger.error("Storage cleanup failed: %r", storage_error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update previous resume: "
                f"{str(e)}"
            ),
        )

    # =====================================================
    # 12. Create Resume database record
    # =====================================================

    resume = Resume(
        candidate_id=candidate.id,
        file_name=safe_filename,
        file_url=file_path,
        file_type=file_type,
        file_size=len(file_data),
        version=new_version,
        is_primary=True,
    )

    db.add(resume)
    db.flush()

    # =====================================================
    # 13. Save AI analysis (within same transaction)
    # =====================================================

    try:

        save_cv_analysis(
            db=db,
            resume_id=resume.id,
            analysis_result=analysis_result,
        )

        # Flush to assign IDs before commit
        db.flush()

        logger.info("AI analysis record created.")

    except Exception as e:

        db.rollback()

        logger.error("Failed to save AI analysis: %r", e)

        # Remove uploaded PDF from Supabase Storage
        try:
            (
                supabase.storage
                .from_("resumes")
                .remove([file_path])
            )
        except Exception as storage_error:
            logger.error("Storage cleanup failed: %r", storage_error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save AI analysis: "
                f"{str(e)}"
            ),
        )

    # =====================================================
    # 14. Commit everything together
    # =====================================================

    try:

        db.commit()
        db.refresh(resume)

    except Exception as e:

        db.rollback()

        logger.error("Database commit failed: %r", e)

        # Remove uploaded file because database
        # save failed

        try:

            (
                supabase.storage
                .from_("resumes")
                .remove([file_path])
            )

        except Exception as storage_error:

            logger.error("Storage cleanup failed: %r", storage_error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save resume information: "
                f"{str(e)}"
            ),
        )

    # =====================================================
    # 15. Return Resume
    # =====================================================

    return resume


# =========================================================
# GET MY RESUMES
# =========================================================

@router.get(
    "/resumes",
    response_model=list[ResumeResponse],
)
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =====================================================
    # 1. Find candidate
    # =====================================================

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
            detail="Candidate profile not found",
        )

    # =====================================================
    # 2. Get candidate resumes
    # =====================================================

    resumes = (
        db.query(Resume)
        .filter(
            Resume.candidate_id == candidate.id
        )
        .order_by(
            Resume.version.desc()
        )
        .all()
    )

    return resumes


# =========================================================
# DOWNLOAD RESUME
# =========================================================

@router.get(
    "/resumes/{resume_id}/download"
)
def download_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =====================================================
    # 1. Find candidate
    # =====================================================

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
            detail="Candidate profile not found",
        )

    # =====================================================
    # 2. Find resume
    # =====================================================

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.candidate_id == candidate.id,
        )
        .first()
    )

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    # =====================================================
    # 3. Create signed URL
    # =====================================================

    try:

        result = (
            supabase.storage
            .from_("resumes")
            .create_signed_url(
                resume.file_url,
                3600,
            )
        )

        signed_url = None

        # -------------------------------------------------
        # Supabase Python client versions can return
        # different key names
        # -------------------------------------------------

        if isinstance(result, dict):

            signed_url = result.get(
                "signedURL"
            )

            if not signed_url:

                signed_url = result.get(
                    "signedUrl"
                )

        if not signed_url:

            raise Exception(
                "Supabase did not return a signed URL. "
                f"Response: {result}"
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create download URL: "
                f"{str(e)}"
            ),
        )

    # =====================================================
    # 4. Return download information
    # =====================================================

    return {
        "file_name": resume.file_name,
        "version": resume.version,
        "is_primary": resume.is_primary,
        "download_url": signed_url,
    }
