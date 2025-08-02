from pydantic import BaseModel
from datetime import date, datetime

class Event(BaseModel):
    ticker: str
    date: date # For date only