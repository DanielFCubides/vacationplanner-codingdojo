from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SearchParamsInputModel(BaseModel):
    origin: str
    destination: str
    arrival_date: datetime
    return_date: datetime
    passengers: Optional[int] = Field(default=1)
    checked_baggage: Optional[int] = Field(default=0)
    carry_on_baggage: Optional[int] = Field(default=0)
    currency: Optional[str] = Field(default="COP")


class Inputs(BaseModel):
    airline: str
    search_params: SearchParamsInputModel
