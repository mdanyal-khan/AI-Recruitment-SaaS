from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.user import User

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


# =========================
# CREATE COMPANY
# =========================

@router.post(
    "",
    response_model=CompanyResponse
)
def create_company(
    data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    company = Company(
        name=data.name,
        description=data.description,
        website=data.website,
        industry=data.industry,
        location=data.location,
        logo_url=data.logo_url
    )

    db.add(company)
    db.flush()

    membership = CompanyMember(
        company_id=company.id,
        user_id=current_user.id,
        role="OWNER"
    )

    db.add(membership)

    db.commit()
    db.refresh(company)

    return company


# =========================
# GET ALL COMPANIES (User's companies)
# =========================

@router.get(
    "",
    response_model=list[CompanyResponse]
)
def get_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all companies where the current user is a member"""
    companies = (
        db.query(Company)
        .join(CompanyMember)
        .filter(CompanyMember.user_id == current_user.id)
        .all()
    )
    return companies


# =========================
# GET SINGLE COMPANY
# =========================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse
)
def get_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single company (user must be a member)"""
    # Check if user is member of this company
    membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id
        )
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this company"
        )
    
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    return company


# =========================
# UPDATE COMPANY
# =========================

@router.put(
    "/{company_id}",
    response_model=CompanyResponse
)
def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update company (only OWNER can update)"""
    # Check if user is OWNER of this company
    owner_membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.role == "OWNER"
        )
        .first()
    )
    
    if not owner_membership:
        raise HTTPException(
            status_code=403,
            detail="Only company owner can update company details"
        )
    
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    return company


# =========================
# DELETE COMPANY
# =========================

@router.delete("/{company_id}")
def delete_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete company (only OWNER can delete)"""
    # Check if user is OWNER of this company
    owner_membership = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == current_user.id,
            CompanyMember.role == "OWNER"
        )
        .first()
    )
    
    if not owner_membership:
        raise HTTPException(
            status_code=403,
            detail="Only company owner can delete company"
        )
    
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    db.delete(company)
    db.commit()
    
    return {
        "message": "Company deleted successfully"
    }