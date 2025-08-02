

# tech = yf.Sector('technology')
# indus = tech.industries
# software = yf.Industry('software-infrastructure').top_companies
# print(software)
# print(tech.top_etfs)
# software = yf.Industry('software-infrastructure')
# dct = software.top_companies.to_dict()
# companies:dict = dct['name']

# res = dict() 
# res_list = list(companies.keys())
# print(res_list[:5])
import yfinance as yf

# Replace 'AAPL' with your desired stock ticker symbol
ticker = yf.Ticker('AAPL')
data = ticker.history(period='1d')
current_price = data['Close'][0]
print(f"Current Price: {current_price}")


# S&P 500 Index (ticker: ^GSPC)
# sp500 = yf.Ticker("^NSEI")

# # Get historical market data
# hist = sp500.history(period="5d")

# print(hist)

# tkr = yf.Ticker("ADBE")
# print(tkr.quarterly_earnings)
# df = tkr.balance_sheet
# print(df.describe())
# news = yf.Search("NVDA", news_count=10).news
# screener = yf.Screener()

# results = screener.get_screeners('day_gainers', count=10)
# for stock in results:
#     print(stock)

# print(news)
# Common information
# print(tech.top_companies)
# tech.key
# tech.name
# tech.symbol
# tech.ticker
# tech.overview
# tech.top_companies
# tech.research_reports

# Sector information
# tech.top_etfs
# tech.top_mutual_funds
# tech.industries

# Industry information
# software.sector_key
# software.sector_name
# print(software.top_performing_companies)
# print(software.top_growth_companies)



# ticker = yf.Ticker("ADBE")
# earnings = ticker.get_fast_info().day_high

# print(earnings)










