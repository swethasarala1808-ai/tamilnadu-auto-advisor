import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

print("🚀 Starting Scan")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Load tickers
df = pd.read_csv("tickers.csv")
tickers = df["ticker"].tolist()
print(f"Loaded {len(tickers)} tickers")

results = []
BATCH_SIZE = 50

for i in range(0, len(tickers), BATCH_SIZE):
    batch = tickers[i:i + BATCH_SIZE]
    print(f"\n🔎 Processing batch {i//BATCH_SIZE+1}: {len(batch)} tickers")

    try:
        data = yf.download(
            batch,
            period="2d",
            interval="1d",
            progress=False,
            threads=True
        )
    except Exception as e:
        print("❌ Download error:", e)
        continue

    # Fix single ticker format
    if isinstance(data.columns, pd.Index):
        data = pd.concat({batch[0]: data}, axis=1)

    # Evaluate each ticker
    for ticker in batch:
        try:
            d = data[ticker]

            if len(d) < 2:
                print(f"⚠️ Not enough data for {ticker}")
                continue

            prev_day = d.iloc[-2]
            today = d.iloc[-1]

            cond1 = today["Close"] > prev_day["Close"]
            cond2 = today["Volume"] > prev_day["Volume"]
            cond3 = today["Close"] > today["Open"]

            if cond1 and cond2 and cond3:
                score = (today["Close"] - today["Open"]) / today["Open"]

                results.append({
                    "symbol": ticker,
                    "open": float(today["Open"]),
                    "close": float(today["Close"]),
                    "volume": int(today["Volume"]),
                    "score": float(score)
                })

                print(f"✔ MATCH: {ticker} ({round(score*100, 2)}%)")

            else:
                print(f"❌ No match: {ticker}")

        except Exception as e:
            print(f"❌ Error {ticker}: {e}")

# Save candidates.csv
df_out = pd.DataFrame(results)
df_out.to_csv("candidates.csv", index=False)
print("\n📄 candidates.csv saved.")

# Save best pick
if len(results) > 0:
    best = max(results, key=lambda x: x["score"])
    print("🏆 Best pick:", best["symbol"])

    with open("data/today_pick.json", "w") as f:
        json.dump(best, f, indent=4)

else:
    print("❌ No picks found today.")

    with open("data/today_pick.json", "w") as f:
        json.dump({"message": "No pick today"}, f)

print("✅ today_pick.json updated")
