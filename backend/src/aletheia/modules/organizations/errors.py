from fastapi import status

from aletheia.core.errors import AppError


class OrganizationNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "ORGANIZATION_NOT_FOUND"
    message = "The organization does not exist or you do not have access to it."


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."
