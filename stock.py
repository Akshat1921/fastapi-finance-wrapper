import csv
import json
import os
import yfinance as yf
import json
import requests
import pandas as pd
import requests
import json


class Data_Retriever:
    
    ticker_dict = None
    companies = dict()
    
    def __init__(self, filename) -> None:
        self.filename = filename
        self.ticker_extractor()
    
    def ticker_extractor(self):
        with open(self.filename, mode='r') as file:
            csv_reader = csv.DictReader(file)
            data_list = []
            for row in csv_reader:
                data_list.append(row)
        ticker_list = dict()
        for data in data_list:
            market_cap = data['Market Cap']
            market_cap = int(float(market_cap))/1000000000 
            ticker_list[data['Symbol']] = [data['Name'], data['Sector'], data['Industry'], data['Country'], market_cap]
        Data_Retriever.ticker_dict = ticker_list
        
    def company_overview(self, ticker):
        tkr = self.get_ticker(ticker)
        info = tkr.info
        del info['companyOfficers']
        return info
        # return tkr.info['longBusinessSummary']
        # if tkr not in self.companies.keys:
        #     self.companies[tkr] = tkr.info['longBusinessSummary']
    
    def historical_data(self, ticker, period):
        tkr = self.get_ticker(ticker)
        hist = tkr.history(period=period)
        return hist
    
    def get_balance_sheet(self, ticker):
        tkr = yf.Ticker(ticker)
        df_str = tkr.balance_sheet.astype(str)
        dct = df_str.to_dict()
        balance_sheet = {k.strftime('%Y-%m-%d'): v for k, v in dct.items()}
        return balance_sheet
        
    def get_ticker(self, ticker):
        return yf.Ticker(ticker)
    
    def get_news(self, ticker):
        tkr = self.get_ticker(ticker)
        return tkr.get_news
    
    def get_cashflow(self, ticker):
        tkr = self.get_ticker(ticker)
        df_str = tkr.cash_flow.astype(str)
        dct = df_str.to_dict()
        cashflow = {k.strftime('%Y-%m-%d'): v for k, v in dct.items()}
        return cashflow
    
    def get_shareholders(self, ticker):
        
        tkr = self.get_ticker(ticker)
        institutional_holders = tkr.institutional_holders.to_dict()
        major_holders = tkr.institutional_holders.to_dict()
        
        del institutional_holders['Date Reported']
        del major_holders['Date Reported']
        
        return {'major-holders': major_holders,
                        'institutional-holders': institutional_holders}
        
    def get_income_statement(self, ticker):
        tkr = self.get_ticker(ticker)
        df_str = tkr.income_stmt.astype(str)
        dct = df_str.to_dict()
        income_stmt = {k.strftime('%Y-%m-%d'): v for k, v in dct.items()}
        return income_stmt
    
    def convert_timestamp(self, df: pd.DataFrame):
        dct = df.to_dict()
        return {k.strftime('%Y-%m-%d'): v for k, v in dct.items()}
    
    def sector_wise_grouping(self, sector):
        sector_dict = dict()
        for key , val in self.ticker_dict.items():
            if val[1] == sector:
                if key not in sector_dict:
                    sector_dict[key] = []
                sector_dict[key].append(self.ticker_dict[key])
        return sector_dict
    
    def industry_wise_grouping(self, industry):
        industry_dict = dict()
        for key , val in self.ticker_dict.items():
            if val[2] == industry:
                if key not in industry_dict:
                    industry_dict[key] = []
                industry_dict[key].append(self.ticker_dict[key])
        return industry_dict
    
    def get_history(self, ticker):
        ticker = self.get_ticker(ticker)
        history = ticker.history(period="4y", interval="3mo").to_json()
        history = json.loads(history)
        return history
    
    def get_latest_history(self, ticker):
        ticker = self.get_ticker(ticker)
        history = ticker.history(period="1d").to_json()
        history = json.loads(history)
        return history


# path = os.path.join(os.path.dirname(__file__), r"data\nasdaq.csv")
# stocks = Data_Retriever(path)
# # print(stocks.ticker_dict)
# print(stocks.industry_wise_grouping('Computer Software: Prepackaged Software'))

# Real Estate Investment Trusts