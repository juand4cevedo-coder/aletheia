import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

PASSWORD_MIN_LENGTH = 15
PASSWORD_MAX_LENGTH = 128

DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    full_name: DisplayName
    organization_name: DisplayName

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.lower()


class RegisterResponse(BaseModel):
    user_id: uuid.UUID
    organization_id: uuid.UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.lower()


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class CurrentUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
