from typing import Optional, List

from pydantic import BaseModel


class BaseCommunicationRequest(BaseModel):
    email: Optional[List[str]]
    mobile: Optional[str]
    template_slug: Optional[str]
    subject: Optional[str]
    attachment: Optional[str]
    attachment_context: Optional[str]
    on_whatsapp: bool = False
    template_format_kwargs: Optional[dict]


class SendEmailRequest(BaseModel):
    subject: str
    to: List[str]
    cc: Optional[List[str]]
    bcc: Optional[List[str]]
    body: str
