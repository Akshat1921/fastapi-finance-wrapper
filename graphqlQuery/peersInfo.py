from pydantic import BaseModel
# import strawberry
from typing import Optional

class peers_info(BaseModel):
    marketCap: Optional[str]
    open: Optional[str]
    priceToBook: Optional[str]
    beta: Optional[str]
    earningsGrowth: Optional[str]
    shortName: Optional[str]
    longName: Optional[str]
    bookValue: Optional[str]
    priceToBook: Optional[str]
    netIncomeToCommon: Optional[str]
    sharesOutstanding: Optional[str]
    enterpriseValue: Optional[str]
    ebitda: Optional[str]
    currentPrice: Optional[str]
    debtToEquity: Optional[str]
    currentRatio: Optional[str]
    totalRevenue: Optional[str]
    returnOnAssets: Optional[str]
    returnOnEquity: Optional[str]
    fiveYearAvgDividendYield: Optional[str]