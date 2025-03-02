import yfinance as yf

ticker = "AAPL"  # Make sure this is a string, not a list
stock = yf.Ticker(ticker)

# Fetch stock info
info = stock.info

# Print the stock name and market price
print(f"Stock: {ticker}")
print(f"Current Price: {info.get('currentPrice', 'N/A')}")
