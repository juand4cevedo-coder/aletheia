import enum

from aletheia.modules.cases.models import CaseRole


class CasePermission(enum.StrEnum):
    READ = "case:read"
    UPDATE = "case:update"
    MANAGE_MEMBERS = "case:manage_members"


CASE_ROLE_PERMISSIONS: dict[CaseRole, frozenset[CasePermission]] = {
    CaseRole.LEAD: frozenset(CasePermission),
    CaseRole.EDITOR: frozenset({CasePermission.READ, CasePermission.UPDATE}),
    CaseRole.VIEWER: frozenset({CasePermission.READ}),
}


def case_permissions_for(role: CaseRole) -> frozenset[CasePermission]:
    return CASE_ROLE_PERMISSIONS[role]
