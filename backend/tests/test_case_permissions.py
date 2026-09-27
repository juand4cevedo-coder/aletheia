from aletheia.modules.cases.models import CaseRole
from aletheia.modules.cases.permissions import (
    CASE_ROLE_PERMISSIONS,
    CasePermission,
    case_permissions_for,
)


def test_every_case_role_has_a_permission_set() -> None:
    assert set(CASE_ROLE_PERMISSIONS) == set(CaseRole)


def test_lead_has_every_case_permission() -> None:
    assert case_permissions_for(CaseRole.LEAD) == frozenset(CasePermission)


def test_editor_can_update_but_not_manage_members() -> None:
    editor = case_permissions_for(CaseRole.EDITOR)

    assert CasePermission.UPDATE in editor
    assert CasePermission.MANAGE_MEMBERS not in editor


def test_viewer_can_only_read() -> None:
    assert case_permissions_for(CaseRole.VIEWER) == frozenset(
        {CasePermission.READ, CasePermission.EVIDENCE_READ}
    )


def test_viewer_cannot_add_evidence() -> None:
    assert CasePermission.EVIDENCE_CREATE not in case_permissions_for(CaseRole.VIEWER)
