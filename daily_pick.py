import yfinance as yf
import json
import pandas as pd

# Load tickers list
tickers = pd.read_csv("tickers.csv")["symbol"].tolist()

BEST = None

def score_stock(symbol):
    try:
        data = yf.download(symbol, period="6d", interval="1d")
        if data.empty:
            return None

        close = data["Close"]
        momentum = (close.iloc[-1] - close.iloc[-3]) / close.iloc[-3] * 100
        volatility = close.pct_change().std()

        if volatility == 0 or pd.isna(volatility):
            return None

        score = momentum / volatility
        return {
            "symbol": symbol,
            "price": float(close.iloc[-1]),
            "momentum": float(momentum),
            "score": float(score)
        }
    except:
        return None


results = []
for t in tickers:
    s = score_stock(t)
    if s:
        results.append(s)

# Save scores for debugging
pd.DataFrame(results).to_csv("candidates.csv", index=False)

# Pick BEST stock overall (no amount yet)
results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)

if len(results_sorted) > 0:
    BEST = results_sorted[0]
else:
    BEST = {"error": "No valid stock found."}

# Save best pick
with open("today_pick.json", "w") as f:
    json.dump(BEST, f, indent=2)

print("Daily pick saved:", BEST)
