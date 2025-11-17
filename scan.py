import yfinance as yf
import pandas as pd
import json
import numpy as np

def expected_intraday_profit(ticker):
    try:
        data = yf.download(ticker, period="30d", interval="1d", progress=False)

        if data.empty:
            return None

        data["intraday"] = (data["Close"] - data["Open"]) / data["Open"]

        avg_return = data["intraday"].tail(20).mean()      # Last 20 days
        momentum = (data["Close"].iloc[-1] -
                    data["Close"].iloc[-5]) / data["Close"].iloc[-5]

        score = (0.7 * avg_return) + (0.3 * momentum)
        return round(score * 100, 4)

    except:
        return None


def scan():
    df = pd.read_csv("tickers.csv")
    results = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        score = expected_intraday_profit(ticker)

        if score is not None:
            results.append({
                "ticker": ticker,
                "score": score
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    best = results[0]

    # Current price (for buy price)
    price = yf.Ticker(best["ticker"]).history(period="1d")["Open"].iloc[-1]

    output = {
        "ticker": best["ticker"],
        "buy_price": float(price),
        "expected_profit_percentage": best["score"]
    }

    with open("today_pick.json", "w") as f:
        json.dump(output, f, indent=4)

    print("✔ Today’s best pick saved!")
    return output


if __name__ == "__main__":
    scan()
