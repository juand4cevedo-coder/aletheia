import enum

from aletheia.modules.organizations.models import MembershipRole


class Permission(enum.StrEnum):
    ORGANIZATION_READ = "organization:read"
    ORGANIZATION_UPDATE = "organization:update"
    MEMBER_READ = "member:read"
    MEMBER_INVITE = "member:invite"
    MEMBER_REMOVE = "member:remove"
    SUBSCRIPTION_READ = "subscription:read"
    AUDIT_READ = "audit:read"
    CASE_CREATE = "case:create"


ROLE_PERMISSIONS: dict[MembershipRole, frozenset[Permission]] = {
    MembershipRole.OWNER: frozenset(Permission),
    MembershipRole.ADMIN: frozenset(
        {
            Permission.ORGANIZATION_READ,
            Permission.ORGANIZATION_UPDATE,
            Permission.MEMBER_READ,
            Permission.MEMBER_INVITE,
            Permission.MEMBER_REMOVE,
            Permission.SUBSCRIPTION_READ,
            Permission.AUDIT_READ,
        }
    ),
    MembershipRole.LAWYER: frozenset(
        {
            Permission.ORGANIZATION_READ,
            Permission.MEMBER_READ,
            Permission.CASE_CREATE,
        }
    ),
    MembershipRole.COLLABORATOR: frozenset({Permission.ORGANIZATION_READ}),
    MembershipRole.AUDITOR: frozenset(
        {
            Permission.ORGANIZATION_READ,
            Permission.MEMBER_READ,
            Permission.AUDIT_READ,
        }
    ),
}


def permissions_for(role: MembershipRole) -> frozenset[Permission]:
    return ROLE_PERMISSIONS[role]
