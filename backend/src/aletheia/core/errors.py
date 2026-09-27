import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from aletheia.core.request_id import REQUEST_ID_HEADER, get_request_id

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[ErrorDetail] | None = None


class AppError(Exception):
    """Base class for errors that are safe to expose to API clients."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."


class ServiceUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "SERVICE_UNAVAILABLE"
    message = "The service is temporarily unavailable."


_HTTP_ERROR_CODES = {
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
}


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    request_id = get_request_id(request)
    body = ErrorResponse(code=code, message=message, request_id=request_id, details=details)
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(exclude_none=True),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def _handle_app_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return _error_response(request, status_code=exc.status_code, code=exc.code, message=exc.message)


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    details = [
        ErrorDetail(field=".".join(str(part) for part in error["loc"]), message=error["msg"])
        for error in exc.errors()
    ]
    return _error_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="VALIDATION_ERROR",
        message="The request contains invalid data.",
        details=details,
    )


async def _handle_http_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    return _error_response(
        request,
        status_code=exc.status_code,
        code=_HTTP_ERROR_CODES.get(exc.status_code, "HTTP_ERROR"),
        message=str(exc.detail),
    )


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error (request_id=%s)", get_request_id(request), exc_info=exc)
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=AppError.code,
        message=AppError.message,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_error)
    app.add_exception_handler(Exception, _handle_unexpected_error)
