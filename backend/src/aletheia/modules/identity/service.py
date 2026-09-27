from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.core.database import violated_constraint
from aletheia.core.security import hash_password
from aletheia.modules.identity.errors import EmailAlreadyRegisteredError
from aletheia.modules.identity.models import User
from aletheia.modules.identity.schemas import RegisterRequest, RegisterResponse
from aletheia.modules.organizations.models import Membership, MembershipRole, Organization


def register_account(session: Session, request: RegisterRequest) -> RegisterResponse:
    """Create a user, their organization and an owner membership in one transaction."""
    user = User(
        email=request.email,
        full_name=request.full_name,
        password_hash=hash_password(request.password),
    )
    organization = Organization(name=request.organization_name)

    try:
        session.add_all([user, organization])
        session.flush()
        session.add(
            Membership(organization_id=organization.id, user_id=user.id, role=MembershipRole.OWNER)
        )
        session.commit()
    except IntegrityError as error:
        session.rollback()
        if violated_constraint(error) == "uq_users_email":
            raise EmailAlreadyRegisteredError() from error
        raise

    return RegisterResponse(user_id=user.id, organization_id=organization.id)
