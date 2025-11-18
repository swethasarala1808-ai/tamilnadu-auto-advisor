# fetch_tickers.py
import requests
import pandas as pd
import io
import time

def fetch_nse():
    # NSE publishes a CSV-like page. We try common endpoints. This may change over time.
    urls = [
        "https://www1.nseindia.com/content/equities/EQUITY_L.csv",
        "https://www.nseindia.com/content/equities/EQUITY_L.csv"
    ]
    for u in urls:
        try:
            resp = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            if resp.status_code == 200 and resp.text.strip():
                df = pd.read_csv(io.StringIO(resp.text))
                return df
        except Exception as e:
            print("NSE fetch error:", e)
            time.sleep(1)
    raise RuntimeError("Could not fetch NSE list. Try again later or run manually.")

def fetch_bse():
    # BSE CSV of companies
    url = "https://www.bseindia.com/downloads1/List_of_companies.csv"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.encoding = 'utf-8'
    if resp.status_code == 200:
        df = pd.read_csv(io.StringIO(resp.text))
        return df
    raise RuntimeError("Could not fetch BSE list. Try again later.")

def build_tickers_csv(output_path="tickers.csv"):
    # NSE
    try:
        nse_df = fetch_nse()
        # NSE file contains SYMBOL column
        if "SYMBOL" in nse_df.columns:
            nse_symbols = nse_df["SYMBOL"].astype(str).str.strip().tolist()
        elif "symbol" in nse_df.columns:
            nse_symbols = nse_df["symbol"].astype(str).str.strip().tolist()
        else:
            nse_symbols = []
        nse_out = [{"ticker": s + ".NS", "exchange": "NSE"} for s in nse_symbols if s]
    except Exception as e:
        print("Skip NSE:", e)
        nse_out = []

    # BSE
    try:
        bse_df = fetch_bse()
        # BSE CSV layout may have 'SC_CODE' and 'SC_NAME' or 'Security Code' / 'Security Id'
        if "Security Id" in bse_df.columns or "Security ID" in bse_df.columns:
            # security id column likely with NSE tickers; fallback:
            col = [c for c in bse_df.columns if "Security" in c][0]
            bse_symbols = bse_df[col].astype(str).str.strip().tolist()
        elif "SC_CODE" in bse_df.columns:
            # SC_CODE are numeric codes — map to symbol may be tricky. Use 'SC_NAME' or 'Security ID'
            if "SC_NAME" in bse_df.columns:
                bse_symbols = bse_df["SC_NAME"].astype(str).str.strip().tolist()
            else:
                bse_symbols = []
        else:
            # fallback: try first column with string values
            bse_symbols = bse_df.iloc[:,0].astype(str).str.strip().tolist()
        # Convert to .BO format where possible — many entries already include codes not symbols.
        # We'll attempt to keep non-empty and append .BO for basic usage.
        bse_out = []
        for s in bse_symbols:
            s_clean = s.split()[0].replace('&','').replace('/','-').strip()
            if s_clean:
                bse_out.append({"ticker": s_clean + ".BO", "exchange": "BSE"})
    except Exception as e:
        print("Skip BSE:", e)
        bse_out = []

    # Combine, dedupe
    combined = nse_out + bse_out
    df = pd.DataFrame(combined).drop_duplicates(subset=["ticker"])
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(df)} tickers to {output_path}")

if __name__ == "__main__":
    build_tickers_csv()
