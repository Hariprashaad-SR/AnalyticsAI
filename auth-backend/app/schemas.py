from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID

class SignupRequest(BaseModel):
    name : str
    email : EmailStr
    password : str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be blank.")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class LoginRequest(BaseModel):
    email : EmailStr
    password : str


class UserOut(BaseModel):
    id : UUID
    name : str
    email : str
    pic : str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    user : UserOut
