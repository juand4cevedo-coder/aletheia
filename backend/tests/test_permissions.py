import pytest

from aletheia.modules.organizations.models import MembershipRole
from aletheia.modules.organizations.permissions import ROLE_PERMISSIONS, Permission, permissions_for


def test_every_role_has_a_permission_set() -> None:
    assert set(ROLE_PERMISSIONS) == set(MembershipRole)


def test_owner_has_every_permission() -> None:
    assert permissions_for(MembershipRole.OWNER) == frozenset(Permission)


def test_admin_manages_members_but_cannot_create_cases() -> None:
    admin = permissions_for(MembershipRole.ADMIN)

    assert Permission.MEMBER_INVITE in admin
    assert Permission.CASE_CREATE not in admin


@pytest.mark.parametrize("role", [MembershipRole.COLLABORATOR, MembershipRole.AUDITOR])
def test_read_only_roles_cannot_modify_the_organization(role: MembershipRole) -> None:
    permissions = permissions_for(role)

    assert Permission.ORGANIZATION_UPDATE not in permissions
    assert Permission.MEMBER_INVITE not in permissions
    assert Permission.MEMBER_REMOVE not in permissions
