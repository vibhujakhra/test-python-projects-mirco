from distutils.log import error
from pydantic import BaseModel
from typing import Optional


class AssestUploadResponse(BaseModel):
    status_code: int
    document_url: Optional[str]
    old_document_url: Optional[str] = None
    error_message: Optional[str]


class ValidationResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str]
