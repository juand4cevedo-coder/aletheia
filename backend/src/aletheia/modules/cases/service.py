import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.core.database import violated_constraint
from aletheia.modules.cases.errors import (
    CaseMemberAlreadyExistsError,
    CaseMemberNotFoundError,
    LastCaseLeadError,
    OrganizationMemberNotFoundError,
)
from aletheia.modules.cases.models import Case, CaseCounter, CaseMember, CaseRole
from aletheia.modules.cases.permissions import case_permissions_for
from aletheia.modules.cases.schemas import (
    CaseCreate,
    CaseDetail,
    CaseMemberAdd,
    CaseMemberSummary,
    CaseSummary,
    CaseUpdate,
)
from aletheia.modules.identity.models import User
from aletheia.modules.organizations.models import Membership

# --- cases -------------------------------------------------------------------


def format_reference(year: int, number: int) -> str:
    return f"CAS-{year}-{number:06d}"


def _next_case_number(session: Session, organization_id: uuid.UUID, year: int) -> int:
    """Atomically reserve the next case number for an organization and year.

    The upsert locks the counter row until the transaction ends, so concurrent
    requests get consecutive numbers instead of duplicates.
    """
    statement = (
        insert(CaseCounter)
        .values(organization_id=organization_id, year=year, last_number=1)
        .on_conflict_do_update(
            index_elements=[CaseCounter.organization_id, CaseCounter.year],
            set_={"last_number": CaseCounter.last_number + 1},
        )
        .returning(CaseCounter.last_number)
    )
    return session.execute(statement).scalar_one()


def create_case(
    session: Session, organization_id: uuid.UUID, creator_id: uuid.UUID, data: CaseCreate
) -> CaseDetail:
    year = datetime.now(UTC).year
    number = _next_case_number(session, organization_id, year)
    case = Case(
        organization_id=organization_id,
        reference=format_reference(year, number),
        title=data.title,
        description=data.description,
        created_by=creator_id,
    )
    session.add(case)
    session.flush()
    session.add(
        CaseMember(
            case_id=case.id,
            user_id=creator_id,
            organization_id=organization_id,
            role=CaseRole.LEAD,
        )
    )
    session.commit()
    return to_detail(case, CaseRole.LEAD)


def list_cases_for_member(
    session: Session, organization_id: uuid.UUID, user_id: uuid.UUID
) -> list[CaseSummary]:
    rows = session.execute(
        select(Case, CaseMember.role)
        .join(CaseMember, CaseMember.case_id == Case.id)
        .where(Case.organization_id == organization_id, CaseMember.user_id == user_id)
        .order_by(Case.created_at.desc(), Case.id)
    ).all()
    return [
        CaseSummary(
            id=case.id,
            reference=case.reference,
            title=case.title,
            status=case.status,
            my_role=role,
            created_at=case.created_at,
        )
        for case, role in rows
    ]


def update_case(session: Session, case: Case, data: CaseUpdate) -> None:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    session.commit()


def to_detail(case: Case, role: CaseRole) -> CaseDetail:
    return CaseDetail(
        id=case.id,
        reference=case.reference,
        title=case.title,
        status=case.status,
        my_role=role,
        created_at=case.created_at,
        description=case.description,
        updated_at=case.updated_at,
        my_permissions=sorted(case_permissions_for(role)),
    )


# --- case members ------------------------------------------------------------


def list_case_members(session: Session, case_id: uuid.UUID) -> list[CaseMemberSummary]:
    rows = session.execute(
        select(CaseMember, User)
        .join(User, User.id == CaseMember.user_id)
        .where(CaseMember.case_id == case_id)
        .order_by(User.full_name, User.id)
    ).all()
    return [_member_summary(member, user) for member, user in rows]


def add_case_member(session: Session, case: Case, data: CaseMemberAdd) -> CaseMemberSummary:
    user = session.scalars(
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.organization_id == case.organization_id, User.id == data.user_id)
    ).one_or_none()
    if user is None:
        raise OrganizationMemberNotFoundError()

    member = CaseMember(
        case_id=case.id,
        user_id=user.id,
        organization_id=case.organization_id,
        role=data.role,
    )
    try:
        session.add(member)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        if violated_constraint(error) == "pk_case_members":
            raise CaseMemberAlreadyExistsError() from error
        raise
    return _member_summary(member, user)


def change_case_member_role(
    session: Session, case: Case, user_id: uuid.UUID, role: CaseRole
) -> CaseMemberSummary:
    _lock_case(session, case.id)
    member, user = _get_case_member(session, case.id, user_id)
    if member.role is CaseRole.LEAD and role is not CaseRole.LEAD:
        _ensure_another_lead_remains(session, case.id)
    member.role = role
    session.commit()
    return _member_summary(member, user)


def remove_case_member(session: Session, case: Case, user_id: uuid.UUID) -> None:
    _lock_case(session, case.id)
    member, _ = _get_case_member(session, case.id, user_id)
    if member.role is CaseRole.LEAD:
        _ensure_another_lead_remains(session, case.id)
    session.delete(member)
    session.commit()


def _lock_case(session: Session, case_id: uuid.UUID) -> None:
    """Serialize membership changes on one case, so two requests cannot remove the last lead."""
    session.execute(select(Case.id).where(Case.id == case_id).with_for_update())


def _get_case_member(
    session: Session, case_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[CaseMember, User]:
    row = session.execute(
        select(CaseMember, User)
        .join(User, User.id == CaseMember.user_id)
        .where(CaseMember.case_id == case_id, CaseMember.user_id == user_id)
        .execution_options(populate_existing=True)
    ).one_or_none()
    if row is None:
        raise CaseMemberNotFoundError()
    member, user = row
    return member, user


def _ensure_another_lead_remains(session: Session, case_id: uuid.UUID) -> None:
    leads = session.scalar(
        select(func.count())
        .select_from(CaseMember)
        .where(CaseMember.case_id == case_id, CaseMember.role == CaseRole.LEAD)
    )
    if (leads or 0) <= 1:
        raise LastCaseLeadError()


def _member_summary(member: CaseMember, user: User) -> CaseMemberSummary:
    return CaseMemberSummary(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=member.role,
        added_at=member.added_at,
    )
