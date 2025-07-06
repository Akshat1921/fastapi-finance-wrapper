import asyncio
import os
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from stock import Data_Retriever
from fastapi.responses import JSONResponse
import yfinance as yf
from fastapi import FastAPI


path = os.path.join("content","nasdaq.csv")
stocks = Data_Retriever(path)



app = FastAPI()

@app.get("/stocks")
async def get_all_stocks(page:int = 1):
    data = stocks.ticker_dict
    limit = 300
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
                # 'shareholders': stocks.get_shareholders(ticker),
                'income-statement': stocks.get_income_statement(ticker)
            }
    
    return JSONResponse(data)

@app.get('/stocks/income-statement/ticker')
async def get_income_statement(ticker):
    return JSONResponse(stocks.get_income_statement(ticker))

@app.get('/stocks/balance-sheet/ticker')
async def get_balance_sheet(ticker):
    return JSONResponse(stocks.get_balance_sheet(ticker))

@app.get('/stocks/cashflow/ticker')
async def get_cashflow(ticker):
    return JSONResponse(stocks.get_cashflow(ticker))

@app.get('/stocks/history/ticker')
async def get_history(ticker):
    combined_history = stocks.get_history(ticker)
    latest_history = stocks.get_latest_history(ticker)
    
    res = {"combined-history":combined_history, "latest-history":latest_history}
    
    return JSONResponse(res)

@app.get('/stocks/peers/sector/{sector}')
async def get_company_by_sector(sector):
    return JSONResponse(stocks.sector_wise_grouping(sector))

# @app.get('/stocks/peers/industry/{industry}',  response_model=List[peers_info])
# async def get_company_by_industry(industry: str) -> List[str]:
#     """Fetch top tickers based on industry."""
#     print(industry)
#     tickers = peers.topFivePeers(industry)
#     print(tickers)
#     results = []
#     for ticker in tickers:
#         tkr = yf.Ticker(ticker)
#         info = tkr.info
#         # Remove unwanted fields
#         info.pop('companyOfficers', None)
#         info.pop('52WeekChange', None)
#         # Map fields to PeersInfo
#         valid_fields = {
#             field: str(info.get(field)) if isinstance(info.get(field), (int, float)) else info.get(field)
#             for field in peers_info.__annotations__.keys()
#         }
#         results.append(peers_info(**valid_fields).model_dump())
#     return JSONResponse(results)


# @strawberry.type
# class Query:
#     @strawberry.field
#     def get_company_overview(self, ticker: str) -> CompanyOverview:
#         tkr = yf.Ticker(ticker)
#         info = tkr.info
#         del info['companyOfficers']
#         del info['52WeekChange']
#         valid_fields = {field: info.get(field) for field in CompanyOverview.__annotations__.keys()}
#         return CompanyOverview(**valid_fields)

#     @strawberry.field
#     async def get_companies_by_industry(self, industry: str) -> List[peers_info]:
#         """Fetch company information for the top tickers in the industry."""
#         # Call the FastAPI endpoint to get tickers
#         tickers = await get_company_by_industry(industry)
        
#         # Fetch details for each ticker using yfinance
#         results = []
#         for ticker in tickers:
#             tkr = yf.Ticker(ticker)
#             info = tkr.info
#             # Remove unwanted fields
#             info.pop('companyOfficers', None)
#             info.pop('52WeekChange', None)
#             # Map fields to PeersInfo
#             valid_fields = {field: info.get(field) for field in peers_info.__annotations__.keys()}
#             results.append(peers_info(**valid_fields))
        
#         return results


# schema = strawberry.Schema(Query)

# graphql_app = GraphQLRouter(schema)
# app.include_router(graphql_app, prefix="/graphql")


    

if __name__ == "__main__":   
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
