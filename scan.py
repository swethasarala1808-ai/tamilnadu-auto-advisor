import yfinance as yf
import pandas as pd
import json
import os

def get_best_stock():
    df = pd.read_csv("tickers.csv")
    tickers = df["ticker"].tolist()

    print(f"Loaded {len(tickers)} tickers")

    best_ticker = None
    best_change = -999

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="2d", interval="1d", progress=False)

            # Need exactly two rows
            if len(data) < 2:
                continue

            # Extract values (float)
            prev_close = float(data["Close"].iloc[-2])
            today_close = float(data["Close"].iloc[-1])
            today_open = float(data["Open"].iloc[-1])
            today_vol = float(data["Volume"].iloc[-1])
            prev_vol = float(data["Volume"].iloc[-2])

            # Conditions
            if today_close > prev_close and today_vol > prev_vol and today_close > today_open:
                change_percent = ((today_close - today_open) / today_open) * 100

                if change_percent > best_change:
                    best_change = change_percent
                    best_ticker = {
                        "symbol": ticker,
                        "open": today_open,
                        "close": today_close,
                        "volume": today_vol,
                        "change": round(change_percent, 2)
                    }

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return best_ticker


def main():
    result = get_best_stock()

    # Ensure data folder exists
    if not os.path.exists("data"):
        os.makedirs("data")

    if result:
        print("Best stock:", result["symbol"])
        with open("data/today_pick.json", "w") as f:
            json.dump(result, f, indent=4)
    else:
        print("No pick today")
        with open("data/today_pick.json", "w") as f:
            json.dump({"message": "No pick today"}, f)


if __name__ == "__main__":
    main()
