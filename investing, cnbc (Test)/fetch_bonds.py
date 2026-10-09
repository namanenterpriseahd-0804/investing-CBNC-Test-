import urllib.request
import json
import sys
from datetime import datetime

DEFAULT_SYMBOLS = ["US10Y", "US2Y", "US5Y", "US30Y"]

def fetch_bond_rates(symbols=DEFAULT_SYMBOLS):
    symbols_param = "|".join(symbols)
    url = f"https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols={symbols_param}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        quotes = data.get("FormattedQuoteResult", {}).get("FormattedQuote", [])
        return quotes

def display_rates(quotes):
    print("=" * 80)
    print(f"{'Symbol':<8} {'Name':<24} {'Yield':<10} {'Change':<10} {'Price':<10} {'Coupon':<8} {'Maturity'}")
    print("=" * 80)
    for q in quotes:
        symbol = q.get("symbol", "")
        name = q.get("name", "")
        yield_rate = q.get("last", "N/A")
        change = f"{q.get('change', '0')} ({q.get('change_pct', '0%')})"
        price = q.get("bond_last_price", "N/A")
        coupon = q.get("coupon", "N/A")
        maturity = q.get("maturity_date", "N/A")
        print(f"{symbol:<8} {name:<24} {yield_rate:<10} {change:<10} {price:<10} {coupon:<8} {maturity}")
    print("=" * 80)

if __name__ == "__main__":
    symbols = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_SYMBOLS
    print(f"Fetching live bond rates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...\n")
    try:
        quotes = fetch_bond_rates(symbols)
        display_rates(quotes)
    except Exception as e:
        print(f"Error fetching bond rates: {e}")
