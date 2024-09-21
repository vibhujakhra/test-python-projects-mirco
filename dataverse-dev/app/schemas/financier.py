from pydantic import BaseModel
from typing import Optional


class FinancierResponse(BaseModel):
    id: int
    name: str


class BankResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
