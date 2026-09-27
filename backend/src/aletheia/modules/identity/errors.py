from fastapi import status

from aletheia.core.errors import AppError


class EmailAlreadyRegisteredError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "EMAIL_ALREADY_REGISTERED"
    message = "An account with this email already exists."
