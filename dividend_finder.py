from sklearn.linear_model import LinearRegression
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# List of top dividend-paying stocks
dividend_stocks = ["KO", "JNJ", "PG", "PEP", "XOM", "CVX", "MCD", "T", "VZ", "PFE"]

def get_dividend_data(stock_symbol):
    """Fetch dividend yield for a stock."""
    stock = yf.Ticker(stock_symbol)
    dividend_yield = stock.info.get("dividendYield", 0)

    return {
        "Stock": stock_symbol,
        "Dividend Yield (%)": round(dividend_yield * 100, 2) if dividend_yield else 0
    }

def rank_dividend_stocks():
    """Ranks stocks based on dividend yield."""
    dividend_data = [get_dividend_data(stock) for stock in dividend_stocks]
    df = pd.DataFrame(dividend_data).sort_values(by="Dividend Yield (%)", ascending=False)
    
    print("\n📊 **Top Dividend Stocks Ranked by Yield** 📊")
    print(df.to_string(index=False))

def predict_dividend_growth(stock_symbol):
    """Predicts future dividend growth based on historical data."""
    stock = yf.Ticker(stock_symbol)
    hist_dividends = stock.dividends

    if hist_dividends.empty or len(hist_dividends) < 5:
        print(f"Not enough dividend data for {stock_symbol}.")
        return None

    # Prepare data for AI model
    X = np.array(range(len(hist_dividends))).reshape(-1, 1)  # Time (years)
    y = hist_dividends.values  # Dividend values

    model = LinearRegression()
    model.fit(X, y)

    future_years = np.array([[len(hist_dividends) + i] for i in range(1, 6)])  # Next 5 years
    predictions = model.predict(future_years)

    return predictions

def plot_dividend_trend(stock_symbol):
    """Plots the historical dividend trend."""
    stock = yf.Ticker(stock_symbol)
    hist_dividends = stock.dividends

    if hist_dividends.empty:
        print(f"No dividend data found for {stock_symbol}.")
        return

    hist_dividends.plot(kind="line", marker="o", title=f"Dividend Trend for {stock_symbol}")
    plt.xlabel("Year")
    plt.ylabel("Dividend Amount ($)")
    plt.grid()
    plt.show()

if __name__ == "__main__":
    rank_dividend_stocks()
    stock_symbol = input("Enter a stock symbol for dividend growth prediction (e.g., JNJ, KO): ").upper()
    predicted_dividends = predict_dividend_growth(stock_symbol)

    if predicted_dividends is not None:
        print("\n📈 **Predicted Dividends for Next 5 Years:**")
        for i, div in enumerate(predicted_dividends, 1):
            print(f"Year {i}: ${round(div, 2)}")

    stock_symbol = input("Enter a stock symbol for dividend visualization (e.g., KO, JNJ): ").upper()
    plot_dividend_trend(stock_symbol)