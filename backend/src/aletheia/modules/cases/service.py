import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from aletheia.modules.cases.models import Case, CaseCounter, CaseMember, CaseRole
from aletheia.modules.cases.schemas import CaseCreate, CaseDetail, CaseSummary


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
    )
