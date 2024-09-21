import uuid
from uuid import UUID

from typing import Optional, List, Dict
from fastapi_users import schemas
from pydantic import BaseModel
from datetime import date



class UserEdit(BaseModel):
    salutation: Optional[str]
    first_name: str
    middle_name: Optional[str] 
    last_name: Optional[str]
    role_id: Optional[int]
    mobile_no: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str ]
    pincode: Optional[str]
    landline_no: Optional[str]
    designation: Optional[str]
    is_active: bool
    email: Optional[str]

class MispDetails(UserEdit):
    pass



class UserRead(schemas.BaseUser[uuid.UUID], UserEdit):
    user_sub_type: Optional[str]
    dob: Optional[date]
    ams_code: Optional[str]
    dealer_code: Optional[str]
    workshop_code: Optional[str]
    insurer_code: Optional[str]
    oem_code: Optional[str]
    misp_code: Optional[str]
    misp_details: Optional[UserEdit]

    # @validator("role_id", always=True)
    # def mutually_exclusive(cls, v, values):
    #     if not values["user_sub_type"] and not v:
    #         raise HTTPException(    
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="ROLE_ID_AND_MISP_SUB_TYPE_ARE_MUTUALLY_EXCLUSIVE",
    #         )
    #     return v

class ModulePermission(BaseModel):
    module_code: str
    module_name: str
    group_name: Optional[str]
    module_url: Optional[str]
    group_url: Optional[str]
    group_code: Optional[str]


class UserModulePermissionResponse(BaseModel):
    user_details: UserRead
    auto_logout_timer: int 
    module_permission: List[ModulePermission]


class RegisteredUser(schemas.BaseUserCreate):
    salutation: str = None
    role_id: Optional[int]
    first_name: str
    middle_name: Optional[str]
    last_name: Optional[str]
    mobile_no: str
    city: Optional[str]
    state: Optional[str ]
    pincode: Optional[str]
    landline_no: Optional[str]
    designation : Optional[str]


class UserCreate(RegisteredUser):
    oem_code: str = None
    insurer_code: str = None
    ams_id: str = None
    user_sub_type: Optional[int]
    dealer_code: str = None
    workshop_code: str = None
    misp_code: str = None


class UserUpdate(schemas.BaseUserUpdate):
    pass


class SendEmailResponse(BaseModel):
    status_code: int
    message: str

class MappedOemResponse(BaseModel):
    misp_email: str
    message: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class AdminRoleRequest(BaseModel):
    role_id: int 
    group_type: Optional[str]
    module: List[ModulePermission]


class UserEditResponse(BaseModel):
    user_id: int
    message: str

class UserRoleListResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]

class UserMetaDataResponse(BaseModel):
    user_id: Optional[UUID]
    oem_code: Optional[str]
    insurer_code: Optional[str]
    ams_code: Optional[str]
    dealer_code: Optional[str]
    workshop_code: Optional[str]
    misp_code : Optional[str]

class MispOemRequest(BaseModel):
    email: str
    oem_code: str
    user_sub_type_id: Optional[int]
