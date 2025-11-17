import pandas as pd

def load_tickers():
    return pd.read_csv("tickers.csv")

def generate():
    df = load_tickers()
    df.to_csv("candidates.csv", index=False)
    print("candidates.csv created!")

if __name__ == "__main__":
    generate()
