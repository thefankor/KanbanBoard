from datetime import datetime

from pydantic import BaseModel, EmailStr


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    username: str
    password: str


class CreateUserResponse(BaseModel):
    email: EmailStr
    name: str
    username: str
    created_at: datetime
    updated_at: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str
