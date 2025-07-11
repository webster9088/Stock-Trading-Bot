import requests
import time

TRADIER_API_KEY = "b2oET9jqnf4M83cY6uoRQlvitvLF"

# === CONFIG ===
MIN_PRICE = 1.00
MAX_PRICE = 50.00
MIN_VOLUME = 500_000
MIN_GAP_PCT = 4.0
SLEEP_SECONDS = 300  # 5 minutes

# === HEADERS ===
HEADERS = {
    "Authorization": f"Bearer {TRADIER_API_KEY}",
    "Accept": "application/json"
}

# === SYMBOL UNIVERSE (expand as needed) ===
SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "INTC",
    "PLTR", "BIDU", "PYPL", "SNAP", "SHOP", "AFRM", "RIVN", "LCID", "SOFI", "FUBO",
    "F", "GM", "T", "XOM", "CVX", "BABA", "NIO", "XPEV", "LI", "RIOT", "MARA",
    "COIN", "UBER", "LYFT", "WMT", "DIS", "TGT", "CRM", "SBUX", "ROKU", "ZM",
    "CVNA", "DKNG", "PENN", "GME", "AMC", "BBBY", "BB", "TLRY", "CGC", "MNMD",
    "ARKK", "SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV", "XLY"
]

def chunk_list(symbols, size):
    for i in range(0, len(symbols), size):
        yield symbols[i:i + size]

def market_is_open():
    try:
        res = requests.get("https://api.tradier.com/v1/markets/clock", headers=HEADERS)
        return res.status_code == 200 and res.json()['clock']['state'] == "open"
    except:
        return False

def get_top_movers():
    candidates = []
    print("Running screener...")

    for chunk in chunk_list(SYMBOLS, 25):  # Tradier allows ~25 symbols per call
        symbols_str = ",".join(chunk)
        res = requests.get(f"https://api.tradier.com/v1/markets/quotes?symbols={symbols_str}", headers=HEADERS)

        if res.status_code != 200:
            print(f"Failed fetch for chunk: {symbols_str}")
            continue

        quotes = res.json().get("quotes", {}).get("quote", [])
        if isinstance(quotes, dict):
            quotes = [quotes]  # handle single result edge case

        for q in quotes:
            try:
                last = float(q["last"])
                prev = float(q["prevclose"])
                vol = int(q["volume"])
                gap_pct = ((last - prev) / prev) * 100

                if MIN_PRICE <= last <= MAX_PRICE and vol > MIN_VOLUME and abs(gap_pct) >= MIN_GAP_PCT:
                    candidates.append({
                        "symbol": q["symbol"],
                        "price": last,
                        "gap%": round(gap_pct, 2),
                        "volume": vol
                    })
            except:
                continue

    return sorted(candidates, key=lambda x: abs(x["gap%"]), reverse=True)

def main():
    print("📈 Starting trading bot with auto-loop...")
    while True:
        if market_is_open():
            print(f"\n[{time.strftime('%H:%M:%S')}] Market is open. Scanning...")
            movers = get_top_movers()
            print(f"Top Candidates: {len(movers)}")
            for stock in movers:
                print(stock)
        else:
            print("Market is closed. Sleeping...")

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
