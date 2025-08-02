import asyncio
import os
import json
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from models.ticker_update_model import TickerUpdate
from peers import Peers_Retriever
from producer import send_updated_stock_to_kafka
from stock import Data_Retriever
from fastapi.responses import JSONResponse
import yfinance as yf
from fastapi.middleware.cors import CORSMiddleware
from graphqlQuery.peersInfo import peers_info
from concurrent.futures import ThreadPoolExecutor
from models.current_price import Event
from datetime import datetime, timedelta, date

NASDAQ_CSV_PATH = os.getenv("NASDAQ_CSV_PATH", os.path.join(os.path.dirname(__file__), "data", "nasdaq.csv"))
SP500_CSV_PATH = os.getenv("SP500_CSV_PATH", os.path.join(os.path.dirname(__file__), "data", "sp500_companies.csv"))

stocks = Data_Retriever(NASDAQ_CSV_PATH)
peers = Peers_Retriever(SP500_CSV_PATH)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stocks")
async def get_all_stocks(page:int = 1):
    data = stocks.ticker_dict
    limit = 253
    all_items = list(data.items())  # Convert dictionary to a list of tuples
    total_items = len(all_items)
    total_pages = (total_items // limit) + (1 if total_items % limit > 0 else 0)
    
    # Calculate the start and end indices for the current page
    start = (page - 1) * limit
    end = start + limit
    
    # Slice the items list to get the items for the current page
    paginated_items = dict(all_items[start:end])
    
    return {
        "items": paginated_items,
        "total": total_items,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None
    }
    

@app.get('/stocks/tickers') 
async def get_tickers():
    return JSONResponse(list(stocks.ticker_dict.keys()))

@app.get("/stocks/company-overview/{ticker}")
async def get_company_info(ticker):
    return JSONResponse(stocks.company_overview(ticker))

def get_financial_data(ticker: str):
    """Reusable function to get financial data for a ticker"""
    def get_company_overview():
        return 'company-overview', stocks.company_overview(ticker)

    def get_balance_sheet():
        return 'balance-sheet', stocks.get_balance_sheet(ticker)

    def get_cashflow():
        return 'cashflow', stocks.get_cashflow(ticker)

    def get_income_statement():
        return 'income-statement', stocks.get_income_statement(ticker)
    
    tasks = [get_company_overview, get_balance_sheet, get_cashflow, get_income_statement]
    
    data = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(task) for task in tasks]
        for future in futures:
            key, value = future.result()
            data[key] = value
    
    return data

@app.get('/stocks/financials/ticker')
async def get_financials(ticker):
    data = get_financial_data(ticker)
    return JSONResponse(data)


def fetch_ticker_info(ticker: str):
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        info.pop('companyOfficers', None)
        info.pop('52WeekChange', None)

        valid_fields = {
            field: str(info.get(field)) if isinstance(info.get(field), (int, float)) else info.get(field)
            for field in peers_info.__annotations__.keys()
        }
        return peers_info(**valid_fields).model_dump()
    except Exception as e:
        print(f"[{ticker}] Error: {e}")
        return None

# Use ThreadPoolExecutor to fetch all in parallel
def fetch_all_in_parallel(ticker_list: List[str]):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_ticker_info, ticker_list))
    return [r for r in results if r is not None]

# Route for Industry
@app.get('/stocks/peers/industry/{industry}')
async def get_company_by_industry(industry: str):
    tickers = peers.top_five_peers_by_industry(industry)
    results = fetch_all_in_parallel(tickers)
    return JSONResponse(results)

# Route for Sector
@app.get('/stocks/peers/sector/{sector}')
async def get_company_by_sector(sector: str):
    tickers = peers.top_five_peers_by_sector(sector)
    results = fetch_all_in_parallel(tickers)
    return JSONResponse(results)

@app.post('/stocks/get_price')
async def get_stock_price(event: Event):
    try:
        # Format dates for yfinance
        end_date = event.date + timedelta(days=1)
        start_str = event.date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Fetch historical close price for the purchase date
        historical_data = yf.download(
            event.ticker,
            start=start_str,
            end=end_str,
            interval='1d',
            progress=False  # Suppresses tqdm in Jupyter/output
        )

        if historical_data.empty:
            return JSONResponse(status_code=400, content={
                "error": f"No historical price data available on {event.date}. "
                         f"It might be a weekend or market holiday."
            })

        purchase_close_price = float(historical_data['Close'].iloc[0])

        # Fetch current price (most recent 1-minute candle)
        ticker_data = yf.Ticker(event.ticker)
        current_data = ticker_data.history(period="1d", interval="1m")

        if current_data.empty:
            return JSONResponse(status_code=200, content={
                "ticker": event.ticker,
                "purchase_price": round(purchase_close_price, 2),
                "current_price": None,
                "message": "Market data not available. It may be a weekend or holiday."
            })

        current_price = float(current_data['Close'].iloc[-1])

        return JSONResponse(status_code=200, content={
            "ticker": event.ticker,
            "purchase_price": round(purchase_close_price, 2),
            "current_price": round(current_price, 2)
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})
    

@app.post("/stocks/get_tickers_update")
async def get_tickers_for_update(tickers: List[TickerUpdate]):
    ticker_list = [ticker.ticker for ticker in tickers]
    results = []
    print(ticker_list)
    for ticker in ticker_list:
        try:
            financial_data = get_financial_data(ticker)
            
            kakfa_message = {
                "ticker": ticker,
                "timestamp": datetime.now().isoformat(),
                "financials": financial_data
            }
            
            send_updated_stock_to_kafka("financial-updates", kakfa_message)
            results.append({"ticker": ticker, "status": "success"})
        except Exception as e:
            results.append({"ticker": ticker, "status": "error", "error": str(e)})
    return JSONResponse({"processed": len(ticker_list), "results": results})
    
    

if __name__ == "__main__":   
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
