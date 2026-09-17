from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.permissions import require_company_role
from app.models.company_member import CompanyMember


router = APIRouter(
    prefix="/permission-test",
    tags=["Permission Test"]
)


@router.get("/{company_id}/owner")
def owner_only(
    company_id: UUID,
    membership: CompanyMember = Depends(
        require_company_role("OWNER")
    )
):
    return {
        "message": "You have OWNER permission",
        "role": membership.role
    }


@router.get("/{company_id}/hr")
def hr_access(
    company_id: UUID,
    membership: CompanyMember = Depends(
        require_company_role(
            "OWNER",
            "HR"
        )
    )
):
    return {
        "message": "You have OWNER or HR permission",
        "role": membership.role
    }


@router.get("/{company_id}/recruiter")
def recruiter_access(
    company_id: UUID,
    membership: CompanyMember = Depends(
        require_company_role(
            "OWNER",
            "HR",
            "RECRUITER"
        )
    )
):
    return {
        "message": "You have company staff permission",
        "role": membership.role
    }