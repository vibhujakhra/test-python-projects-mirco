from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: str
    name: str


class PGDetailResponse(BaseResponse):
    logo_url: str
