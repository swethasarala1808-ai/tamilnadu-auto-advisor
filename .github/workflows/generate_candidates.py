import pandas as pd
import yfinance as yf

# Load your stock list
stocks = pd.read_csv("all_stocks.csv")  # ticker, exchange

candidates = []

for ticker in stocks["ticker"]:
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="5m")  # intraday
        if data.empty:
            continue
        current_price = data['Close'][-1]
        high_price_today = data['High'].max()
        potential_profit = high_price_today - current_price
        candidates.append({
            "ticker": ticker,
            "current_price": current_price,
            "max_shares": 1000,  # placeholder
            "potential_profit": potential_profit
        })
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

df_candidates = pd.DataFrame(candidates)
df_candidates.to_csv("candidates.csv", index=False)
print("✅ candidates.csv generated")
