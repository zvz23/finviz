from playwright.sync_api import sync_playwright, Page
from db import FinvizDB
from dotenv import load_dotenv
import time
import json
import os

load_dotenv()

FINVIZ_HOME_URL = "https://finviz.com/"
FINVIZ_NEWS_URL = "https://finviz.com/news.ashx"
FINVIZ_LOGIN_URL = "https://finviz.com/login.ashx"

FINVIZ_EMAIL = os.environ.get("FINVIZ_EMAIL")
FINVIZ_PASSWORD = os.environ.get("FINVIZ_PASSWORD")

DB_NAME = 'finviz.db'

source_with_embed = [
    "yahoo.com",
    "nytimes.com",
    "foxbusiness.com",
    "bbc.com",
    "cnbc.com"
]


def get_news_urls(news_page: Page):
    news_page.bring_to_front()
    base_news_sel = news_page.wait_for_selector("table.news_time-table > tbody >tr:nth-child(2) > td:nth-child(1) > table")
    news_a_tags = base_news_sel.query_selector_all("tr a")
    news_urls = [i.get_attribute("href") for i in news_a_tags]
    return news_urls

def get_tickers(tickers_page: Page):
    tickers_page.bring_to_front()
    signal_one_container_sel = tickers_page.query_selector("#js-signals_1")
    signal_two_container_sel = tickers_page.query_selector("#js-signals_2")
    signals_sels = []
    signals_sels.extend(signal_one_container_sel.query_selector_all("tr"))
    signals_sels.extend(signal_two_container_sel.query_selector_all("tr"))
    obj = {
        "tickers": [],
        "tickers_only": []
    }
    for signal_sel in signals_sels:
        ticker = {
            "ticker": signal_sel.evaluate("signal_sel => signal_sel.children[0].innerText"),
            "last": signal_sel.evaluate("signal_sel => signal_sel.children[1].innerText"),
            "change": signal_sel.evaluate("signal_sel => signal_sel.children[2].innerText"),
            "volume": signal_sel.evaluate("signal_sel => signal_sel.children[3].innerText"),
            "signal": signal_sel.evaluate("signal_sel => signal_sel.children[5].innerText")
        }
        obj["tickers"].append(ticker)
    
    signals_only_sels = tickers_page.query_selector_all("table.hp_signal-table tbody > tr")
    for signal_only_sel in signals_only_sels:
        first_ticker = signal_only_sel.evaluate("signal_only_sel => signal_only_sel.children[0].innerText")
        second_ticker = signal_only_sel.evaluate("signal_only_sel => signal_only_sel.children[1].innerText")
        tickers_signal_only = {
            'tickers': [first_ticker, second_ticker],
            'signal': signal_only_sel.evaluate("signal_only_sel => signal_only_sel.children[2].innerText")
        }
        obj["tickers_only"].append(tickers_signal_only)
    return obj

def get_futures():
    pass

def login(page: Page):
    page.bring_to_front()
    while True:
        try:
            page.goto(FINVIZ_LOGIN_URL, wait_until="domcontentloaded")
            email_input = page.wait_for_selector("input[name='email']", timeout=5000)
            password_input = page.wait_for_selector("input[name='password']", timeout=5000)
            submit_button = page.wait_for_selector("input[type='submit']", timeout=5000)
            email_input.click()
            email_input.type(FINVIZ_EMAIL)
            password_input.click()
            password_input.type(FINVIZ_PASSWORD)
            submit_button.click()
            page.wait_for_selector("#js-signals_1", timeout=6000)
            break
        except:
            print("THERE WAS A PROBLEM LOGGING IN")
            pass

    

    
def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = b.new_context(no_viewport=True)
        tickers_page = context.new_page()
        login(tickers_page)
        tickers_page.goto(FINVIZ_HOME_URL, wait_until="domcontentloaded")
        news_page = context.new_page()
        news_page.goto(FINVIZ_NEWS_URL, wait_until="domcontentloaded")
        attempt = 0
        while True:
            attempt += 1
            news = get_news_urls(news_page)
            if news:
                with FinvizDB(DB_NAME) as conn:
                    conn.save_news_many([[i] for i in news])
                    print(f"SAVED {len(news)} NEWS")
            if attempt >= 5:
                obj = get_tickers(tickers_page)
                with open('tickers.json', 'w') as f:
                    json.dump(obj, f)
                print("UPDATE TICKERS")
                attempt = 0
            time.sleep(5)


if __name__ == "__main__":
    main()
