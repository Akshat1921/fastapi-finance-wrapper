import yfinance as yf

tck = yf.Ticker("NVDA")


# get historical market data
income = tck.history(period="4y", interval="3mo")
print(income.to_json())