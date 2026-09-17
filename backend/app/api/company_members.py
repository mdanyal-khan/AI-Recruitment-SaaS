from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.user import User

from app.schemas.company import (
    AddMemberRequest,
    MemberResponse,
)


router = APIRouter(
    prefix="/companies",
    tags=["Company Members"],
)


# =========================================================
# ADD COMPANY MEMBER
# =========================================================

@router.post(
    "/{company_id}/members",
    response_model=MemberResponse,
    status_code=201,
)
def add_member(
    company_id: UUID,
    data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # 1. Check company exists
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    # 2. Check current user is OWNER
    owner_membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.role == "OWNER",
        )
        .first()
    )

    if not owner_membership:
        raise HTTPException(
            status_code=403,
            detail="Only the company owner can add members",
        )

    # 3. Check target user exists
    target_user = None
    if data.email:
        target_user = (
            db.query(User)
            .filter(
                User.email == data.email.strip().lower()
            )
            .first()
        )
        if not target_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with email '{data.email}' not found. Please ask them to register first.",
            )
    elif data.user_id:
        target_user = (
            db.query(User)
            .filter(
                User.id == data.user_id
            )
            .first()
        )
        if not target_user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Either email or user_id must be provided",
        )

    # 4. Check if already a member
    existing_membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == target_user.id,
        )
        .first()
    )

    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this company",
        )

    # 5. Create membership
    membership = CompanyMember(
        company_id=company_id,
        user_id=target_user.id,
        role=data.role,
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return MemberResponse(
        id=membership.id,
        company_id=membership.company_id,
        user_id=membership.user_id,
        role=membership.role,
        email=target_user.email,
        first_name=target_user.first_name,
        last_name=target_user.last_name,
    )


# =========================================================
# GET COMPANY MEMBERS
# =========================================================

@router.get(
    "/{company_id}/members",
    response_model=list[MemberResponse],
)
def get_members(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # 1. Check current user is a member
    membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this company",
        )

    # 2. Get all members
    members = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id
        )
        .all()
    )

    return [
        MemberResponse(
            id=m.id,
            company_id=m.company_id,
            user_id=m.user_id,
            role=m.role,
            email=m.user.email if m.user else None,
            first_name=m.user.first_name if m.user else None,
            last_name=m.user.last_name if m.user else None,
        )
        for m in members
    ]


# =========================================================
# REMOVE COMPANY MEMBER
# =========================================================

@router.delete(
    "/{company_id}/members/{user_id}",
)
def remove_member(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # 1. Check current user is OWNER
    owner_membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.role == "OWNER",
        )
        .first()
    )

    if not owner_membership:
        raise HTTPException(
            status_code=403,
            detail="Only the company owner can remove members",
        )

    # 2. Find target membership
    membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == user_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=404,
            detail="Company member not found",
        )

    # 3. Prevent owner from removing themselves
    if membership.role == "OWNER":
        raise HTTPException(
            status_code=400,
            detail="Company owner cannot be removed",
        )

    # 4. Delete membership
    db.delete(membership)
    db.commit()

    return {
        "message": "Member removed successfully",
    }

