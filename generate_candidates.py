import yfinance as yf
import pandas as pd
import numpy as np

def calculate_score(momentum, vol_std, avg_vol):
    return (momentum * 2000) - (vol_std * 50000) + (avg_vol / 2000)

df = pd.read_csv("tickers.csv")
rows = []

for index, row in df.iterrows():
    ticker = row["ticker"]
    
    try:
        data = yf.download(ticker, period="7d", interval="1d")
        
        if data.empty:
            print(f"No price data for {ticker}")
            continue
        
        close = data["Close"]
        momentum = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
        vol_std = close.pct_change().std()
        avg_vol = data["Volume"].mean()

        score = calculate_score(momentum, vol_std, avg_vol)

        rows.append([
            ticker,
            close.iloc[-1],
            momentum,
            vol_std,
            avg_vol,
            score
        ])

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        continue

if len(rows) == 0:
    raise ValueError("No tickers passed the filter. candidates.csv will not be created.")

df_out = pd.DataFrame(rows, columns=["ticker", "latest", "momentum", "vol_std", "avg_vol", "score"])
df_out = df_out.sort_values("score", ascending=False)
df_out.to_csv("candidates.csv", index=False)

print("candidates.csv created successfully!")
