import yfinance as yf

# Define the ticker symbol (e.g., Apple Inc.)
ticker_symbol = "TTE.PA"

# Get ticker data
ticker = yf.Ticker(ticker_symbol)

# Get historical prices for the last 30 days
historical_data = ticker.history(period="252d")

# Print historical prices
print(historical_data)