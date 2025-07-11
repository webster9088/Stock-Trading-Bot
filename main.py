import requests
import time

TRADIER_API_KEY = "b2oET9jqnf4M83cY6uoRQlvitvLF"

# === CONFIG ===
MIN_PRICE = 1.00
MAX_PRICE = 50.00
MIN_VOLUME = 500_000
MIN_GAP_PCT = 4.0

# === HEADERS ===
HEADERS = {
    "Authorization": f"Bearer {TRADIER_API_KEY}",
    "Accept": "application/json"
}

# === FUNCTION: CHECK IF MARKET IS OPEN ===
def market_is_open():
    res = requests.get("https://api.tradier.com/v1/markets/clock", headers=HEADERS)
    if res.status_code != 200:
        print("Error checking market status")
        return False
    return res.json()['clock']['state'] == "open"

# === FUNCTION: FETCH TOP MOVERS ===
def get_top_movers():
    print("Fetching top movers...")
    url = "https://api.tradier.com/v1/markets/etfs/quotes"  # We’ll use ETF universe as proxy for now
    symbols = ["SPY", "QQQ", "IWM", "DIA", "XLF", "XLK", "ARKK"]  # Replace with your watchlist or real screener later
    query = ",".join(symbols)
    res = requests.get(f"https://api.tradier.com/v1/markets/quotes?symbols={query}", headers=HEADERS)

    if res.status_code != 200:
        print("Error fetching quotes:", res.text)
        return []

    quotes = res.json()["quotes"]["quote"]
    candidates = []

    for q in quotes:
        symbol = q["symbol"]
        last = float(q["last"])
        prev_close = float(q["prevclose"])
        volume = int(q["volume"])
        gap_pct = ((last - prev_close) / prev_close) * 100

        if MIN_PRICE <= last <= MAX_PRICE and volume > MIN_VOLUME and abs(gap_pct) >= MIN_GAP_PCT:
            candidates.append({
                "symbol": symbol,
                "price": last,
                "gap%": round(gap_pct, 2),
                "volume": volume
            })

    return sorted(candidates, key=lambda x: abs(x["gap%"]), reverse=True)

# === MAIN LOOP ===
def main():
    print("Starting trading bot...")
    if market_is_open():
        print("Market is open. Running screener...")
        movers = get_top_movers()
        print(f"Top Candidates: {len(movers)}")
        for stock in movers:
            print(stock)
    else:
        print("Market is closed. Sleeping...")

if __name__ == "__main__":
    main()
