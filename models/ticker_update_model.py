from pydantic import BaseModel
from datetime import datetime

class TickerUpdate(BaseModel):
    ticker: str