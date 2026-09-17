from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.models.candidate import Candidate



from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse
)


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)




@router.post(
    "/profile",
    response_model=CandidateResponse,
    status_code=201
)
def create_candidate_profile(
    candidate_data: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_candidate = (
        db.query(Candidate)
        .filter(
            Candidate.user_id == current_user.id
        )
        .first()
    )

    if existing_candidate:
        raise HTTPException(
            status_code=400,
            detail="Candidate profile already exists"
        )

    candidate = Candidate(
        user_id=current_user.id,
        **candidate_data.model_dump()
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate




@router.get(
    "/profile",
    response_model=CandidateResponse
)
def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
            detail="Candidate profile not found"
        )

    return candidate




@router.put(
    "/profile",
    response_model=CandidateResponse
)
def update_candidate_profile(
    candidate_data: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
            detail="Candidate profile not found"
        )

    update_data = candidate_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)

    return candidate