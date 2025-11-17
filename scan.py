import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def load_tickers():
    return pd.read_csv("tickers.csv")

def get_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            return None
        return float(data["Close"].iloc[-1])
    except:
        return None

def scan():
    df = load_tickers()
    results = []

    for _, row in df.iterrows():
        ticker = row["ticker"]

        price = get_price(ticker)
        if price is not None:
            results.append({
                "ticker": ticker,
                "price": price,
                "score": round(price % 100, 2)   # Simple scoring
            })

    if not results:
        raise Exception("No prices found!")

    best = sorted(results, key=lambda x: x["score"], reverse=True)[0]

    with open("today_pick.json", "w") as f:
        json.dump(best, f, indent=4)

    return best

if __name__ == "__main__":
    print(scan())
