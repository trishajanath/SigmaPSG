from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    name: str
    email: EmailStr
    disabled: Optional[bool] = None

class UserCreate(User):
    password: str

    @field_validator("name")
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        if len(value) < 3 or len(value) > 25:
            raise ValueError("Name must be between 3 and 25 characters")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 5 or len(value) > 20:
            raise ValueError("Password must be between 5 and 20 characters")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value

class UserRead(User):
    pass

class UserInDB(User):
    hashed_password: str

    @classmethod
    def create_user(cls, user_create: UserCreate) -> 'UserInDB':
        hashed_password = pwd_context.hash(user_create.password)
        return UserInDB(
            username=user_create.username,
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password
        )
