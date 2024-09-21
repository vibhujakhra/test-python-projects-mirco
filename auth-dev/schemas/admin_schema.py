from pydantic import BaseModel
from typing import List, Optional


class RoleRequestSchema(BaseModel):
    group_type: str
    role_name: str
    is_active: bool
    module_ids: List[int]
    creator_editor: str
    has_create_update_access: bool
    
class RoleUpdateSchema(BaseModel):
    creator_editor: str
    role_id: int
    has_create_update_access: bool
    is_active: bool
    module_ids: List[int]
    
    
class RoleListResponse(BaseModel):
    role_id: int
    group_code: str
    role_name: str
    group_type: str
    status: bool
    has_create_update_access: bool
    module_ids: List[int]


class UserRequestBase(BaseModel):
    salutation: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    designation: Optional[str]
    email: str
    mobile_no: str
    landline_no: Optional[str]

    #user_meta_data
    dealer_code: str
    workshop_code: Optional[str]

class DealerUserRequest(UserRequestBase):
    relationship_manager_email: str

class BrokingSalesUserRequest(UserRequestBase):
    region: Optional[str]
    employee_code: str
    # reportee_emails: List[str] = None


class WorkshopUserRequest(UserRequestBase):
    employee_code: str
    relationship_manager_email: str
    workshop_code: str


class OemUserRequest(UserRequestBase):
    employee_code: str
    workshop_code: str
    oem_code: str
    relationship_manager_email: str

class BrokingClaimsUserRequest(UserRequestBase):
    employee_code: str
    dealer_code: Optional[str]
    workshop_code: str

class BrokingOpsUserRequest(UserRequestBase):
    employee_code: str
    reporting_manager_email: str


class HelpDeskUserRequest(UserRequestBase):
    employee_code: str 
    reporting_manager_email: str
    workshop_code: str
    insurer_code: str


class ICUserRequest(UserRequestBase):
    employee_code: str
    insurer_code: str
    workshop_code: str
    address: str
    relationship_manager_email: str


class UserCreateRequest(BaseModel):
    creator_editor: Optional[str]
    admin_role_id: int
    salutation: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    designation: Optional[str]
    email: str
    mobile_no: str
    landline_no: Optional[str]
    region: Optional[str]
    address: Optional[str]

    employee_code: Optional[str]
    region: Optional[str]

    #user_meta_data
    dealer_code: str
    workshop_code: Optional[str]
    oem_code: Optional[str]
    insurer_code: Optional[str]

    #relationship_mangager
    relationship_manager_id: Optional[str]

    #reportees
    reportee_ids: List[str] = None
    reporting_manager_id: Optional[str]


class UserUpdateRequest(BaseModel):
    creator_editor: Optional[str]
    user_id: str
    admin_role_id: Optional[int]
    salutation: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    mobile_no: Optional[str]
    landline_no: Optional[str]
    email: Optional[str]
    address: Optional[str]
    designation: Optional[str]
    employee_code: Optional[str]
    region: Optional[str]
    is_active: Optional[bool]
    address: Optional[str]
    insurer_code: Optional[str]

    #relationship_mangager
    relationship_manager_id: Optional[str]

    #reportees
    reportee_ids: List[str] = None
    reporting_manager_id: Optional[str]

    #user_meta_data
    dealer_code: Optional[str]
    workshop_code: Optional[str]
    oem_code: Optional[str]
    

class StatusUpdateSchema(BaseModel):
    role_id: Optional[int]
    user_id: Optional[str]
    is_active: Optional[bool]
    