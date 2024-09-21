from typing import Optional

from pydantic import BaseModel


class GenerateCancellationRequest(BaseModel):
    cancellation_number: str
    is_cancellation_letter: bool


class GenerateCancellationResponse(BaseModel):
    status: str
    cancellation_download_url: Optional[str]


class GenerateCancellationValidationErrorResponse(BaseModel):
    status: str
    message: list
