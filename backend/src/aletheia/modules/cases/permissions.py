import enum

from aletheia.modules.cases.models import CaseRole


class CasePermission(enum.StrEnum):
    READ = "case:read"
    UPDATE = "case:update"
    MANAGE_MEMBERS = "case:manage_members"
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_CREATE = "evidence:create"


CASE_ROLE_PERMISSIONS: dict[CaseRole, frozenset[CasePermission]] = {
    CaseRole.LEAD: frozenset(CasePermission),
    CaseRole.EDITOR: frozenset(
        {
            CasePermission.READ,
            CasePermission.UPDATE,
            CasePermission.EVIDENCE_READ,
            CasePermission.EVIDENCE_CREATE,
        }
    ),
    CaseRole.VIEWER: frozenset({CasePermission.READ, CasePermission.EVIDENCE_READ}),
}


def case_permissions_for(role: CaseRole) -> frozenset[CasePermission]:
    return CASE_ROLE_PERMISSIONS[role]
