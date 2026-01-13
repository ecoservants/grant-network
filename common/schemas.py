from pydantic import BaseModel, Field
from typing import Optional

class Funder(BaseModel):
    ein: str = Field(..., pattern=r"^\d{9}$")
    name: str
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    ntee_code: Optional[str] = None
