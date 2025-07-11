import time
import requests

def check_market_open():
    response = requests.get("https://api.tradier.com/v1/markets/clock",
                            headers={"Authorization": "Bearer YOUR_API_KEY_HERE",
                                     "Accept": "application/json"})
    if response.status_code == 200:
        market = response.json()['clock']
        return market['state'] == 'open'
    return False

def main():
    print("Starting trading bot...")
    if check_market_open():
        print("Market is open. Screener and strategy logic goes here.")
    else:
        print("Market is closed. Sleeping...")
    time.sleep(10)

if __name__ == "__main__":
    main()
