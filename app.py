import matplotlib
matplotlib.use("Agg", force=True)

from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os


app = Flask(__name__)

# Ensure 'static' folder exists for saving images
if not os.path.exists("static"):
    os.makedirs("static")

# Sector-based dividend stock list
sector_stocks = {
    "Tech": ["AAPL", "MSFT", "NVDA", "GOOGL"],
    "Finance": ["JPM", "BAC", "WFC", "GS"],
    "Energy": ["XOM", "CVX", "COP", "SLB"],
    "Consumer Goods": ["KO", "PEP", "PG", "MCD"]
}

def get_dividend_data(stock_symbol):
    """Fetch dividend yield and history for a given stock."""
    stock = yf.Ticker(stock_symbol)
    hist_dividends = stock.dividends

    if not isinstance(hist_dividends, pd.Series) or hist_dividends.empty:
        print(f"Error: No valid dividend data for {stock_symbol}, received: {hist_dividends}")
        return None

    latest_dividend = hist_dividends.iloc[-1] if not hist_dividends.empty else 0
    dividend_yield = stock.info.get("dividendYield", None)

    if dividend_yield is None:
        print(f"Warning: No dividend yield found for {stock_symbol}")
        return None

    return {
        "Stock": stock_symbol,
        "Latest Dividend": latest_dividend,
        "Dividend Yield (%)": round(dividend_yield * 100, 2)
    }

def plot_dividend_trend(stock_symbol):
    """Generates a dividend trend graph and saves it as an image."""
    try:
        stock = yf.Ticker(stock_symbol)
        hist_dividends = stock.dividends

        if hist_dividends.empty:
            return None

        # Ensure non-interactive backend (no Tkinter dependency)
        plt.switch_backend("Agg")

        fig, ax = plt.subplots(figsize=(6, 4))
        hist_dividends.plot(kind="line", marker="o", ax=ax, title=f"Dividend Trend for {stock_symbol}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Dividend Amount ($)")
        ax.grid()

        image_path = f"static/{stock_symbol}_dividends.png"
        fig.savefig(image_path, format="png", bbox_inches="tight")
        plt.close(fig)  # Close figure to free memory

        return image_path
    except Exception as e:
        print(f"Error plotting dividend trend for {stock_symbol}: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    image_path = None
    risk_level = None
    sector_rankings = rank_sector_dividends()

    if request.method == "POST":
        stock_symbol = request.form["stock_symbol"].upper()
        data = get_dividend_data(stock_symbol)
        risk_level = get_dividend_risk(stock_symbol)
        image_path = plot_dividend_trend(stock_symbol) if data else None

    return render_template("index.html", data=data, risk_level=risk_level, image_path=image_path, sector_rankings=sector_rankings)

def get_dividend_risk(stock_symbol):
    """Analyzes if a stock is at risk of cutting dividends."""
    stock = yf.Ticker(stock_symbol)
    hist_dividends = stock.dividends

    if hist_dividends.empty or len(hist_dividends) < 5:
        return "Insufficient data"

    # Check if dividends are decreasing over the last 5 payouts
    last_dividends = hist_dividends.tail(5).values  # Get last 5 dividend values
    risk_level = "Low"

    if last_dividends[-1] < last_dividends[0]:  # If the most recent dividend is lower than 5 payouts ago
        risk_level = "High"
    elif last_dividends[-1] < last_dividends[-2]:  # If latest dividend is lower than the previous one
        risk_level = "Medium"

    return risk_level

def rank_sector_dividends():
    """Ranks dividend stocks within each sector by yield."""
    sector_ranking = {}

    for sector, stocks in sector_stocks.items():
        dividend_data = [get_dividend_data(stock) for stock in stocks]
        
        # Filter out None values
        dividend_data = [data for data in dividend_data if data is not None]

        if not dividend_data:  # If no valid data, skip this sector
            print(f"Warning: No valid dividend data for sector {sector}")
            sector_ranking[sector] = []
            continue

        df = pd.DataFrame(dividend_data)

        if "Dividend Yield (%)" not in df.columns:  # Avoid KeyError
            print(f"Error: 'Dividend Yield (%)' column missing in sector {sector}")
            sector_ranking[sector] = []
            continue

        df = df.sort_values(by="Dividend Yield (%)", ascending=False)
        sector_ranking[sector] = df.to_dict(orient="records")

    return sector_ranking

if __name__ == "__main__":
    import os
    os.environ["MPLBACKEND"] = "Agg"  # Extra safeguard for Matplotlib
    app.run(debug=False, use_reloader=False, threaded=False)
