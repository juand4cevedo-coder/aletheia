import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.modules.organizations.models import Organization

pytestmark = pytest.mark.integration


def test_organization_is_persisted_with_generated_id_and_timestamps(db_session: Session) -> None:
    organization = Organization(name="Firma de prueba")
    db_session.add(organization)
    db_session.commit()

    stored = db_session.get(Organization, organization.id)

    assert stored is not None
    assert isinstance(stored.id, uuid.UUID)
    assert stored.id.version == 4
    assert stored.created_at.tzinfo is not None
    assert stored.updated_at.tzinfo is not None


def test_organization_name_cannot_be_blank(db_session: Session) -> None:
    db_session.add(Organization(name="   "))

    with pytest.raises(IntegrityError, match="ck_organizations_name_not_blank"):
        db_session.flush()
