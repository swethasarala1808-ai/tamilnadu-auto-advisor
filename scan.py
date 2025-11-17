import yfinance as yf
import pandas as pd
import json

def scan():
    df = pd.read_csv("candidates.csv")

    # Sort by intraday score
    df = df.sort_values("score", ascending=False)

    best = df.iloc[0]
    ticker = best["ticker"]

    # Current price
    price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]

    final = {
        "ticker": ticker,
        "current_price": float(price),
        "score": float(best["score"])
    }

    with open("today_pick.json", "w") as f:
        json.dump(final, f, indent=4)

    print("✔ Today’s pick saved!")
    return final

if __name__ == "__main__":
    scan()
