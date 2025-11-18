# scan.py
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import time
from datetime import datetime

# CONFIG
TICKERS_CSV = "tickers.csv"
OUT_DIR = "data"
CANDIDATES_CSV = os.path.join(OUT_DIR, "candidates.csv")
TODAY_JSON = os.path.join(OUT_DIR, "today_pick.json")
BATCH_SIZE = 200     # number of tickers per yf.download call (tune as needed)
TOP_N = 10           # produce top 10 candidates
SLEEP_BETWEEN_BATCH = 1.0  # seconds

# Ensure output dir exists
os.makedirs(OUT_DIR, exist_ok=True)

def load_tickers():
    df = pd.read_csv(TICKERS_CSV)
    if "ticker" in df.columns:
        return df["ticker"].dropna().astype(str).tolist()
    # fallback: assume single column
    return df.iloc[:,0].dropna().astype(str).tolist()

def score_batch(tickers):
    """
    Download last 2 days for tickers in a single batch, compute simple score:
    score = % change from yesterday close to today close.
    Returns list of dicts: symbol, price, change_percent, score
    """
    out = []
    try:
        # yfinance supports downloading many tickers at once
        data = yf.download(tickers, period="2d", interval="1d", progress=False, threads=True)
        # if single ticker, data columns shape differs
        if data.empty:
            return out

        # If multi-ticker, columns are multiindex (Open,Close,...)
        if isinstance(data.columns, pd.MultiIndex):
            # parse per ticker
            for tk in tickers:
                try:
                    # safe access
                    if ("Close", tk) in data.columns:
                        closes = data["Close", tk].dropna()
                    else:
                        # try dataframe slice by ticker
                        closes = data.xs(tk, axis=1, level=1)["Close"].dropna()
                    if len(closes) < 2:
                        continue
                    today = float(closes.iloc[-1])
                    prev = float(closes.iloc[-2])
                    change = ((today - prev) / prev) * 100
                    out.append({
                        "symbol": tk,
                        "price": today,
                        "change": round(change, 4),
                        "score": round(change, 6)
                    })
                except Exception:
                    continue
        else:
            # single ticker case: data['Close'] is series with two rows
            try:
                closes = data["Close"].dropna()
                if len(closes) >= 2:
                    today = float(closes.iloc[-1])
                    prev = float(closes.iloc[-2])
                    change = ((today - prev) / prev) * 100
                    out.append({
                        "symbol": tickers[0],
                        "price": today,
                        "change": round(change, 4),
                        "score": round(change, 6)
                    })
            except Exception:
                pass
    except Exception as e:
        print("Batch download error:", e)
    return out

def scan_all():
    tickers = load_tickers()
    print(f"Loaded {len(tickers)} tickers")
    all_results = []
    # chunked processing
    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i:i+BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch)} tickers")
        res = score_batch(batch)
        all_results.extend(res)
        time.sleep(SLEEP_BETWEEN_BATCH)

    if not all_results:
        print("No results found.")
        # write empty outputs to avoid site errors
        pd.DataFrame([]).to_csv(CANDIDATES_CSV, index=False)
        with open(TODAY_JSON, "w") as f:
            json.dump({"date": str(datetime.utcnow().date()), "best_stock": None}, f)
        return

    df = pd.DataFrame(all_results)
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    # Save top candidates
    df.to_csv(CANDIDATES_CSV, index=False)

    # Choose best pick: top row
    best = df.iloc[0].to_dict()
    # Add basic target & stop example (2% target, 0.8% stop)
    buy_price = best["price"]
    best["buy_price"] = round(buy_price, 2)
    best["target_price"] = round(buy_price * 1.02, 2)
    best["stop_loss"] = round(buy_price * 0.992, 2)
    best["reason"] = "top_change"

    with open(TODAY_JSON, "w") as f:
        json.dump({"date": str(datetime.utcnow().date()), "best_stock": best}, f, indent=2)

    print("Scan complete. Best:", best["symbol"])
    return best

if __name__ == "__main__":
    scan_all()
import json

# If results exist, choose the best pick
if len(results) > 0:
    best = results[0]

    pick = {
        "symbol": best["symbol"],
        "open": float(best["open"]),
        "close": float(best["close"]),
        "volume": int(best["volume"])
    }

    # Save to JSON for Streamlit
    with open("data/today_pick.json", "w") as f:
        json.dump(pick, f, indent=4)

    print("Today’s pick saved to today_pick.json")
else:
    # Create empty pick file
    with open("data/today_pick.json", "w") as f:
        json.dump({"message": "No pick today"}, f)

    print("No pick today. Empty file created.")
