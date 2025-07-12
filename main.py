import requests
import time
from datetime import datetime

TRADIER_API_KEY = "I7YVOMB625hYP8QleEUTQAAnAVWZ"
TRADIER_ACCOUNT_ID = "VA63174246"
BASE_URL = "https://sandbox.tradier.com/v1"

# === CONFIG ===
MIN_PRICE = 1.00
MAX_PRICE = 50.00
MIN_VOLUME = 500_000
MIN_GAP_PCT = 4.0
SLEEP_SECONDS = 300  # 5 min
POSITION_SIZE = 1000  # dollars
RISK = 0.01
REWARD = 0.03

HEADERS = {
    "Authorization": f"Bearer {TRADIER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL", "NFLX", "INTC",
    "PLTR", "BIDU", "PYPL", "SNAP", "SHOP", "AFRM", "RIVN", "LCID", "SOFI", "FUBO",
    "F", "GM", "T", "XOM", "CVX", "BABA", "NIO", "XPEV", "LI", "RIOT", "MARA",
    "COIN", "UBER", "LYFT", "WMT", "DIS", "TGT", "CRM", "SBUX", "ROKU", "ZM",
    "CVNA", "DKNG", "PENN", "GME", "AMC", "BBBY", "BB", "TLRY", "CGC", "MNMD",
    "ARKK", "SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV", "XLY"
]

opening_highs = {}

def is_market_open():
    r = requests.get(f"{BASE_URL}/markets/clock", headers=HEADERS)
    return r.ok and r.json()['clock']['state'] == "open"

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def fetch_quotes(symbols):
    all_data = []
    for chunk in chunk_list(symbols, 25):
        s = ",".join(chunk)
        r = requests.get(f"{BASE_URL}/markets/quotes?symbols={s}", headers=HEADERS)
        if not r.ok: continue
        quotes = r.json().get("quotes", {}).get("quote", [])
        if isinstance(quotes, dict): quotes = [quotes]
        all_data.extend(quotes)
    return all_data

def place_trade(symbol, price):
    shares = int(POSITION_SIZE / price)
    stop = round(price * (1 - RISK), 2)
    target = round(price * (1 + REWARD), 2)

    print(f"📈 Executing TRADE: {symbol} | Buy @ {price} | SL: {stop} | TP: {target} | Qty: {shares}")

    order = {
        "class": "oco",
        "type": "market",
        "symbol": symbol,
        "duration": "gtc",
        "side": "buy",
        "quantity": shares,
        "order_to_cancel": {
            "type": "limit",
            "price": target,
            "duration": "gtc",
            "side": "sell"
        },
        "order_to_cancel_2": {
            "type": "stop",
            "stop": stop,
            "duration": "gtc",
            "side": "sell"
        }
    }

    r = requests.post(f"{BASE_URL}/accounts/{TRADIER_ACCOUNT_ID}/orders", headers=HEADERS, data=order)
    if r.ok:
        print(f"✅ Order placed for {symbol}")
    else:
        print(f"❌ Failed to place order for {symbol}: {r.text}")

def main():
    print("📡 Bot started.")
    while True:
        now = datetime.now()
        if not is_market_open():
            print("Market closed. Waiting...")
            time.sleep(SLEEP_SECONDS)
            continue

        print(f"\n[{now.strftime('%H:%M:%S')}] Scanning...")

        quotes = fetch_quotes(SYMBOLS)
        for q in quotes:
            try:
                symbol = q['symbol']
                price = float(q['last'])
                volume = int(q['volume'])
                prev = float(q['prevclose'])
                gap_pct = ((price - prev) / prev) * 100

                if not (MIN_PRICE <= price <= MAX_PRICE and volume >= MIN_VOLUME and abs(gap_pct) >= MIN_GAP_PCT):
                    continue

                if symbol not in opening_highs:
                    opening_highs[symbol] = price
                    continue

                if now.hour == 9 and now.minute < 45:
                    opening_highs[symbol] = max(opening_highs[symbol], price)
                    continue

                if price > opening_highs[symbol]:
                    place_trade(symbol, price)
                    del opening_highs[symbol]  # Avoid repeat
            except Exception as e:
                print(f"Error with {q.get('symbol')}: {e}")

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
