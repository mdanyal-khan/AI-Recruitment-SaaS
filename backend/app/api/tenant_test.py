from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.tenant import get_current_company
from app.models.company import Company


router = APIRouter(
    prefix="/tenant-test",
    tags=["Tenant Test"]
)


@router.get("/{company_id}")
def test_company_access(
    company_id: UUID,
    company: Company = Depends(get_current_company)
):
    return {
        "message": "You can access this company",
        "company_id": str(company.id),
        "company_name": company.name
    }