import yfinance as yf
import pandas as pd
import numpy as np

# List of NSE stocks you want to scan
stocks = ["RELIANCE.NS", "SBIN.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

results = []

for symbol in stocks:
    try:
        data = yf.download(symbol, period="5d", interval="1d")

        # Skip if no data
        if data is None or len(data) < 2:
            continue

        # Reset index
        data = data.reset_index()

        # Extract last 2 days
        prev_day = data.iloc[-2]
        today = data.iloc[-1]

        # ---- FIXED COMPARISONS USING .values ----
        # Example filters (you can adjust logic)

        # 1. Today's close higher than yesterday
        cond1 = (today["Close"] > prev_day["Close"])

        # 2. Today’s volume higher than yesterday
        cond2 = (today["Volume"] > prev_day["Volume"])

        # 3. Bullish candle
        cond3 = (today["Close"] > today["Open"])

        # If all conditions match, add stock
        if cond1 and cond2 and cond3:
            results.append({
                "symbol": symbol.replace(".NS", ""),
                "open": today["Open"],
                "close": today["Close"],
                "volume": today["Volume"]
            })

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Save to CSV
df = pd.DataFrame(results)

# If no stocks found, still create an empty file (very important)
df.to_csv("candidates.csv", index=False)

print("Scan complete. candidates.csv generated.")
