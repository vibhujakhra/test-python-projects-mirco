from pydantic import BaseModel


class SalutationResponse(BaseModel):
    id: int
    name: str
    salutation_type: str


class RelationResponse(BaseModel):
    id: int
    name: str
