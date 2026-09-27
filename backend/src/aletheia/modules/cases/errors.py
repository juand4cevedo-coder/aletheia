from fastapi import status

from aletheia.core.errors import AppError


class CaseNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "CASE_NOT_FOUND"
    message = "The case does not exist or you do not have access to it."
