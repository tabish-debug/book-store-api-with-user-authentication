from datetime import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    photo: Optional[str]

    class Config:
        orm_mode = True

class BookBaseSchema(BaseModel):
    title: str
    description: str
    cover_image: Optional[str]
    price: float

    class Config:
        orm_mode = True

class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    password_confirm: str
    role: str = 'user'
    verified: bool = False

class CreateBookSchema(BookBaseSchema):
    user_id: Optional[str]

class UpdateBookSchema(BaseModel):
    title: Optional[str]
    description: Optional[str]
    cover_image: Optional[str]
    price: Optional[str]

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class BookResponse(BookBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
