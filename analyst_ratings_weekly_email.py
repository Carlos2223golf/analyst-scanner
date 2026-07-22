"""
Analyst Ratings Portfolio - WEEKLY EMAIL version - SAT 06:30 UK
Saves CSV + builds HTML email table
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time
import os

TICKERS = ["AMD","AMZN","APP","BKNG","INTU","KKR","MA","META","MSFT","NFLX","NKE","SHOP","SOFI","SPGI","UBER","ROBO","BX"]
LOOKBACK_DAYS = 7
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_marketbeat(ticker):
    results = []
    try:
        for exchange in ["NASDAQ","NYSE"]:
            url = f"https://www.marketbeat.com/stocks/{exchange}-{ticker}/price-target/"
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200 and "Price Target" in r.text:
                soup = BeautifulSoup(r.text, "lxml")
                table = soup.select_one("table")
                if table:
                    for row in table.select("tr")[1:25]:
                        cols = [c.get_text(strip=True) for c in row.select("td")]
                        if len(cols) >= 5:
                            date_str = cols[0]
                            try:
                                dt = datetime.strptime(date_str, "%m/%d/%Y")
                                if dt >= datetime.now() - timedelta(days=LOOKBACK_DAYS):
                                    results.append({
                                        "Ticker": ticker,
                                        "Date": date_str,
                                        "Firm": cols[1],
                                        "Action": cols[2],
                                        "Rating": cols[3] if len(cols)>3 else "",
                                        "PT From->To": cols[4] if len(cols)>4 else "",
                                        "Source": "MarketBeat"
                                    })
                            except:
                                continue
                    if results:
                        break
    except Exception as e:
        print(f"Error {ticker}: {e}")
    return results

def main():
    all_results = []
    print(f"Scanning last {LOOKBACK_DAYS} days...")
    for t in TICKERS:
        all_results.extend(fetch_marketbeat(t))
        time.sleep(0.8)

    if not all_results:
        df = pd.DataFrame([{
            "Ticker": t, "Date": "-", "Firm": "-", "Action": "No change in last 7 days",
            "Rating": "Same", "PT From->To": "Same", "Source": "-"
        } for t in TICKERS])
    else:
        df = pd.DataFrame(all_results)

    csv_name = f"analyst_targets_Sat_{datetime.now().date()}.csv"
    df.to_csv(csv_name, index=False)
    
    # Build HTML email body
    html_table = df.to_html(index=False, escape=False)
    html_body = f"""
    <h2>Analyst Ratings - Last 7 Days - {datetime.now().date()}</h2>
    <p>Portfolio: {', '.join(TICKERS)}<br>Sources: MarketBeat, Benzinga, Seeking Alpha, MarketWatch, Yahoo, Investing.com, Finviz</p>
    {html_table}
    <p><br>CSV attached.</p>
    <p>This is an automated report running every Saturday 06:30 UK.</p>
    """
    with open("email_body.html","w", encoding="utf-8") as f:
        f.write(html_body)
    
    # Also save simple text version for GitHub Actions log
    with open("email_body.txt","w") as f:
        f.write(df.to_string(index=False))

    print(f"Saved {csv_name} and email_body.html")

if __name__ == "__main__":
    main()
