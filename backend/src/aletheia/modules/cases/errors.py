from fastapi import status

from aletheia.core.errors import AppError


class CaseNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "CASE_NOT_FOUND"
    message = "The case does not exist or you do not have access to it."


class CaseMemberNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "CASE_MEMBER_NOT_FOUND"
    message = "The user is not a member of this case."


class OrganizationMemberNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "ORGANIZATION_MEMBER_NOT_FOUND"
    message = "The user is not a member of this organization."


class CaseMemberAlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "CASE_MEMBER_ALREADY_EXISTS"
    message = "The user is already a member of this case."


class LastCaseLeadError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "LAST_CASE_LEAD"
    message = "A case must keep at least one lead."
