import yfinance as yf
import pandas as pd
import json
import datetime

# Load NSE/BSE tickers
tickers = pd.read_csv("tickers.csv")["symbol"].tolist()

# User investment amount
INVEST_AMOUNT = 300   # you can change this later

def score_stock(ticker):
    try:
        data = yf.download(ticker, period="10d", interval="1d", progress=False)
        if data.empty:
            return None

        # Basic metrics
        price = float(data["Close"].iloc[-1])
        if price > INVEST_AMOUNT:  # skip expensive stocks
            return None

        # Momentum = last close - previous close
        momentum = price - float(data["Close"].iloc[-2])

        # Volatility = standard deviation of 10 days
        volatility = float(data["Close"].pct_change().std())

        # AI Score = momentum * (1 / volatility)
        score = momentum * (1 / (volatility + 1e-6))

        return {
            "ticker": ticker,
            "price": price,
            "momentum": momentum,
            "score": score
        }

    except:
        return None


best_stock = None
best_score = -999999

for t in tickers:
    info = score_stock(t)
    if info and info["score"] > best_score:
        best_score = info["score"]
        best_stock = info

# Save result
if best_stock:
    best_stock["date"] = str(datetime.date.today())
    best_stock["invest_amount"] = INVEST_AMOUNT
    best_stock["qty"] = best_stock["invest_amount"] // best_stock["price"]

    with open("today_pick.json", "w") as f:
        json.dump(best_stock, f, indent=4)
else:
    with open("today_pick.json", "w") as f:
        json.dump({"error": "No suitable stock found"}, f, indent=4)
