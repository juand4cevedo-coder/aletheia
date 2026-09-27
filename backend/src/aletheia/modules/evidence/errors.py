from fastapi import status

from aletheia.core.errors import AppError


class EvidenceNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "EVIDENCE_NOT_FOUND"
    message = "The evidence does not exist or you do not have access to it."


class EmptyFileError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "EMPTY_FILE"
    message = "The uploaded file is empty."


class FileTooLargeError(AppError):
    status_code = status.HTTP_413_CONTENT_TOO_LARGE
    code = "FILE_TOO_LARGE"
    message = "The uploaded file exceeds the maximum allowed size."


class UnsupportedFileTypeError(AppError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    code = "UNSUPPORTED_FILE_TYPE"
    message = "This type of file cannot be preserved as evidence."


class FileTypeMismatchError(AppError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    code = "FILE_TYPE_MISMATCH"
    message = "The file extension does not match the actual content of the file."


class EvidenceAlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "EVIDENCE_ALREADY_EXISTS"
    message = "A file with identical content is already preserved in this case."


class CaseNotActiveError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "CASE_NOT_ACTIVE"
    message = "Evidence can only be added to active cases."


class EvidenceStorageError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "EVIDENCE_STORAGE_UNAVAILABLE"
    message = "The evidence could not be stored. Please try again later."
