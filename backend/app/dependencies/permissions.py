from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.company_member import CompanyMember
from app.models.user import User


def require_company_role(*allowed_roles: str):

    def role_checker(
        company_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> CompanyMember:

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
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this company"
            )

        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return membership

    return role_checker