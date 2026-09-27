from fastapi import status

from aletheia.core.errors import AppError


class EmailAlreadyRegisteredError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "EMAIL_ALREADY_REGISTERED"
    message = "An account with this email already exists."


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"
    message = "The email or password is incorrect."


class NotAuthenticatedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "NOT_AUTHENTICATED"
    message = "Authentication is required to access this resource."
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidRefreshTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_REFRESH_TOKEN"
    message = "The session is no longer valid. Please sign in again."
