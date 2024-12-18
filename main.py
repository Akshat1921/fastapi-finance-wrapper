import asyncio
import os
from fastapi import FastAPI
import uvicorn
from stock import Data_Retriever
from fastapi.responses import JSONResponse

path = os.path.join(os.path.dirname(__file__), r"data\nasdaq.csv")
stocks = Data_Retriever(path)

app = FastAPI()

@app.get("/stocks")
async def get_all_stocks(page:int = 1):
    data = stocks.ticker_dict
    limit = 10
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

@app.get('/stocks/financials/ticker')
async def get_financials(ticker):
    data = {
                'company-overview': stocks.company_overview(ticker),
                'balance-sheet': stocks.get_balance_sheet(ticker),
                'cashflow': stocks.get_cashflow(ticker),
                'shareholders': stocks.get_shareholders(ticker),
                'income-statement': stocks.get_income_statement(ticker)
            }
    
    return JSONResponse(data)


@app.get('/stocks/history/ticker')
async def get_history(ticker):
    combined_history = stocks.get_history(ticker)
    latest_history = stocks.get_latest_history(ticker)
    
    res = {"combined-history":combined_history, "latest-history":latest_history}
    
    return JSONResponse(res)

@app.get('/stocks/peers/sector/{sector}')
async def get_company_by_sector(sector):
    return JSONResponse(stocks.sector_wise_grouping(sector))

@app.get('/stocks/peers/industry/{industry}')
async def get_company_by_industry(industry):
    print(industry)
    print(stocks.industry_wise_grouping(industry))
    return JSONResponse(stocks.industry_wise_grouping(industry))

if __name__ == "__main__":   
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
