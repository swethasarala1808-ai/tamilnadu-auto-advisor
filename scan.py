import yfinance as yf
import pandas as pd
import numpy as np
import json
import math

# -------------------------------------------------
# Load tickers
# -------------------------------------------------
df = pd.read_csv("tickers.csv")
tickers = df["ticker"].tolist()
print(f"Loaded {len(tickers)} tickers")

# -------------------------------------------------
# Batch download (yfinance works best in groups)
# -------------------------------------------------
BATCH_SIZE = 100
results = []

for i in range(0, len(tickers), BATCH_SIZE):
    batch = tickers[i:i + BATCH_SIZE]
    print(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch)} tickers")

    try:
        data = yf.download(
            batch,
            period="2d",
            interval="1d",
            progress=False,
            threads=True
        )

        # If single ticker, wrap into multi-index
        if isinstance(data.columns, pd.Index):
            data = pd.concat({batch[0]: data}, axis=1)

    except Exception as e:
        print("Batch error:", e)
        continue

    # -------------------------------------------------
    # Process each ticker in batch
    # -------------------------------------------------
    for ticker in batch:
        try:
            d = data[ticker]

            # Need 2 days
            if len(d) < 2:
                continue

            prev_day = d.iloc[-2]
            today = d.iloc[-1]

            # Conditions
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

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

# -------------------------------------------------
# Create candidates.csv
# -------------------------------------------------
df_out = pd.DataFrame(results)
df_out.to_csv("candidates.csv", index=False)
print("candidates.csv generated.")

# -------------------------------------------------
# Pick BEST stock
# -------------------------------------------------
if len(results) > 0:
    best = sorted(results, key=lambda x: x["score"], reverse=True)[0]
    print("Scan complete. Best:", best["symbol"])

    # Save today_pick.json
    with open("data/today_pick.json", "w") as f:
        json.dump(best, f, indent=4)
else:
    print("No picks found today.")

    with open("data/today_pick.json", "w") as f:
        json.dump({"message": "No pick today"}, f)

print("today_pick.json updated.")
