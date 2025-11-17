import pandas as pd
import yfinance as yf
import numpy as np

def load_tickers():
    return pd.read_csv("tickers.csv")

def intraday_score(ticker):
    try:
        data = yf.download(ticker, period="15d", interval="1d", progress=False)
        if data.empty:
            return None
        
        data["ret"] = (data["Close"] / data["Open"]) - 1
        score = data["ret"].mean() * 100     # % return
        return round(score, 4)
    except:
        return None

def generate():
    df = load_tickers()
    results = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        score = intraday_score(ticker)

        if score is not None:
            results.append({
                "ticker": ticker,
                "score": score
            })

    df_out = pd.DataFrame(results)
    df_out.to_csv("candidates.csv", index=False)
    print("✔ candidates.csv updated with intraday scores!")

if __name__ == "__main__":
    generate()
