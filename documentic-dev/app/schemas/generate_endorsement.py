from pydantic import BaseModel


class GenerateEndorsementRequest(BaseModel):
    endorsement_number: str


class GenerateEndorsementResponse(BaseModel):
    status: str
    endorsement_download_url: str


class GenerateEndorsementValidationErrorResponse(BaseModel):
    status: str
    message: list
