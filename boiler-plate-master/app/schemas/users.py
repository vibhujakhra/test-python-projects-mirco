from datetime import datetime, date
from typing import Optional, Any

from pydantic import BaseModel, validator


class UserResponse(BaseModel):
    id: int
    code: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    address_line_1: str
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    phone_number: str
    email: str
    date_of_birth: date
    user_type: Any
    gender: Any
    is_active: bool

    @validator("date_of_birth")
    def date_to_str(cls, value):
        return value.strftime("%Y-%m-%d") if value else None


class CreateUserRequest(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    address_line_1: str
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    phone_number: str
    email: str
    date_of_birth: str
    user_type: str
    gender: str

    @validator("date_of_birth")
    def str_to_date(cls, value):
        return datetime.strptime(value, "%Y-%m-%d") if value else None


class UpdateUserRequest(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    date_of_birth: Optional[str]
    user_type: Optional[str]
    gender: Optional[str]

    @validator("date_of_birth")
    def str_to_date(cls, value):
        return datetime.strptime(value, "%Y-%m-%d") if value else None
