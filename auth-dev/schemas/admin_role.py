from pydantic import BaseModel, validator
from typing import Optional, List

class AdminGroupResponse(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool


class AdminRoleResponse(BaseModel):
    id: int
    role_name: str


class RoleListResponse(BaseModel):
    role_name: str
    group_type: str
    status: bool
    has_create_edit_access: bool
    access_modules: List[str]

class ModuleResponse(BaseModel):
    id: int
    name: str
    module_code: Optional[str]
    group_name : Optional[str]
    group_url : Optional[str]
    module_url : Optional[str]
    group_code : Optional[str]
    is_active: bool


class UserListResponse(BaseModel):
    id: Optional[str]
    group_id: Optional[str]
    group_code: Optional[str]
    
    admin_role_id: Optional[str]
    user_name: Optional[str]
    email: Optional[str]
    designation : Optional[str]
    is_active: bool
    salutation: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    employee_code : Optional[str]
    landline_no: Optional[str]
    mobile_no: Optional[str]
    insurance_company: Optional[str]
    insurer_code: Optional[str]
    address: Optional[str]
    region: Optional[str]

    relationship_manager_id: Optional[str]

    reportee_ids: Optional[List[str]] = None
    reporting_manager_id: Optional[str]

    dealer_code: Optional[str]
    workshop_code: Optional[str]
    oem_code: Optional[str]


    @validator("id", pre=True)
    def uuid_to_str(cls, value):
        return str(value)

class UserListRequest(BaseModel):
    email: Optional[str]
    user_name: Optional[str]
    group_type_id: Optional[int]
    group_code: Optional[str]
    user_role_id: Optional[int]


class ManagerResponse(BaseModel):
    id: str
    user_name: str
    email: str
