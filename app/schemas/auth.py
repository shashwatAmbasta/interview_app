from pydantic import BaseModel, EmailStr, Field


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str


class AuthResponse(BaseModel):
    user: UserResponse
