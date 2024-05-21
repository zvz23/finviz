from playwright.sync_api import sync_playwright, Page, Browser
from db import McDonaldsDB
from dotenv import load_dotenv
import time
import json
import os

load_dotenv()

FINVIZ_HOME_URL = "https://finviz.com/"
FINVIZ_NEWS_URL = "https://finviz.com/news.ashx"
FINVIZ_FUTURES_URL = "https://elite.finviz.com/futures.ashx"
FINVIZ_LOGIN_URL = "https://finviz.com/login.ashx"
FILINGRE_HOME_URL = "https://www.filingre.com/"
FILINGRE_NEWS_URL = "https://www.filingre.com/news"
FILINGRE_REPORTS_URL = "https://www.filingre.com/sec-financial-reports"

FILINGRE_EMAIL = os.environ.get('FILINGRE_EMAIL')
FILINGRE_PASSWORD = os.environ.get('FILINGRE_PASSWORD')
FINVIZ_EMAIL = os.environ.get("FINVIZ_EMAIL")
FINVIZ_PASSWORD = os.environ.get("FINVIZ_PASSWORD")

DB_NAME = 'mcdonalds.db'

source_with_embed = [
    "yahoo.com",
    "nytimes.com",
    "foxbusiness.com",
    "bbc.com",
    "cnbc.com"
]

def get_news_finviz(news_page: Page):
    news_page.bring_to_front()
    base_news_sel = news_page.wait_for_selector("table.news_time-table > tbody >tr:nth-child(2) > td:nth-child(1) > table")
    news_a_tags = base_news_sel.query_selector_all("tr a")
    news_urls = [i.get_attribute("href") for i in news_a_tags]
    return news_urls
def get_tickers_finviz(tickers_page: Page):
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
            "tickers": [first_ticker, second_ticker],
            "signal": signal_only_sel.evaluate("signal_only_sel => signal_only_sel.children[2].innerText")
        }
        obj["tickers_only"].append(tickers_signal_only)
    return obj

def get_futures_finviz(futures_page: Page):
    futures_page.bring_to_front()
    futures_container_sels = futures_page.query_selector_all("#futures div.grid > a")
    futures = []
    for future_sel in futures_container_sels:
        try:
            futures.append({
                "ticker": future_sel.query_selector(":scope > :nth-child(2)").inner_text().strip(),
                "price": future_sel.query_selector(":scope > :nth-child(3)").inner_text().strip(),
                "high": future_sel.query_selector(":scope > :nth-child(4) > :nth-child(1) > :nth-child(1) > :nth-child(2)").inner_text().strip(),
                "high_gain": future_sel.query_selector(":scope > :nth-child(4) > :nth-child(1) > :nth-child(2)").inner_text().strip(),
                "low": future_sel.query_selector(":scope >:nth-child(4) > :nth-child(2) > :nth-child(1) > :nth-child(2)").inner_text().strip(),
                "low_gain": future_sel.query_selector(":scope > :nth-child(4) > :nth-child(2) > :nth-child(2)").inner_text().strip(),
            })
        except:
            pass
    return futures

def login_finviz(page: Page):
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

def get_news_filingsre(news_page: Page):
    news_page.bring_to_front()
    news_a_tags = news_page.query_selector_all("div.news-container div.container > div > a")
    news_urls = [i.get_attribute('href') for i in news_a_tags]
    return news_urls

def get_reports_filingre(reports_page: Page):
    reports_page.bring_to_front()
    reports_page.wait_for_selector("#financials-container-reports div.container > div")
    financial_reports_sels = reports_page.query_selector_all("#financials-container-reports div.container > div")
    reports = {
        'financial': [],
        'filings': []
    }
    for report_sel in financial_reports_sels:
        financial_report = {}
        financial_report['symbol'] = report_sel.query_selector("div.list-symbol > h4").inner_text().strip()
        financial_report['name'] = report_sel.query_selector("h4.list-name").inner_text().strip()
        financial_report['report_type'] = report_sel.query_selector("h4[ng-if='data.form']").inner_text().strip()
        financial_report['report_url'] = report_sel.query_selector(":scope > a").get_attribute('href')
        reports["financial"].append(financial_report)

    sec_filings_sels = reports_page.query_selector_all("#financials-container-sec div.container > div")
    for filing_sel in sec_filings_sels:
        filing = {}
        filing['symbol'] = filing_sel.query_selector("div.list-symbol h4").inner_text().strip()
        filing['filing_url'] = filing_sel.eval_on_selector(":scope > a", "node => node.href")
        reports['filings'].append(filing)

    return reports

def login_filingre(news_page: Page):
    while True:
        news_page.bring_to_front()
        news_page.goto(FILINGRE_HOME_URL)
        time.sleep(5)
        try:
            login_button = news_page.wait_for_selector("button#login")
            login_button.click()
        except:
            return
        try:
            email_input = news_page.wait_for_selector("input[name='email']")
            password_input = news_page.wait_for_selector("input[name='password']")
            submit_button = news_page.wait_for_selector("button[name='submit']")
            email_input.type(FILINGRE_EMAIL)
            password_input.type(FILINGRE_PASSWORD)
            submit_button.click()
            news_page.wait_for_url("https://www.filingre.com/overview")
            time.sleep(3)
            break
        except Exception as e:
            print(e)
            print("THERE WAS A PROBLEM LOGGING IN FILINGRE")   

    
def start_bot():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = b.new_context(no_viewport=True)

        # Setup Finviz
        finviz_tickers_page = context.new_page()
        login_finviz(finviz_tickers_page)
        finviz_tickers_page.locator("body").press("End")
        finviz_tickers_page.goto(FINVIZ_HOME_URL, wait_until="domcontentloaded")
        finviz_news_page = context.new_page()
        finviz_news_page.goto(FINVIZ_NEWS_URL, wait_until="domcontentloaded")
        finviz_futures_page = context.new_page()
        finviz_futures_page.goto(FINVIZ_FUTURES_URL, wait_until="domcontentloaded")

        # Setup Filingre
        filingre_news_page = context.new_page()
        filingre_reports_page = context.new_page()
        login_filingre(filingre_news_page)
        filingre_news_page.goto(FILINGRE_NEWS_URL)
        filingre_reports_page.bring_to_front()
        filingre_reports_page.goto(FILINGRE_REPORTS_URL)

        
        
        attempt = 0
        while True:
            attempt += 1
            finviz_news = get_news_finviz(finviz_news_page)
            filingre_news = get_news_filingsre(filingre_news_page)
            if finviz_news:
                with McDonaldsDB(DB_NAME) as conn:
                    conn.save_news_many_finviz([[i] for i in finviz_news])
                    print(f"SAVED {len(finviz_news)} NEWS FROM FINVIZ")

            if filingre_news:
                with McDonaldsDB(DB_NAME) as conn:
                    conn.save_news_many_filingre([[i] for i in filingre_news])
                    print(f"SAVED {len(finviz_news)} NEWS FROM FILINGRE")
             
            if attempt >= 10:
                obj = get_tickers_finviz(finviz_tickers_page)
                with open('tickers_finviz.json', 'w') as f:
                    json.dump(obj, f)
                print("TICKERS UPDATED")
                futures = get_futures_finviz(finviz_futures_page)
                with open("futures_finviz.json", "w") as f:
                    json.dump(futures, f)
                print("FUTURES UPDATED")
                attempt = 0
            time.sleep(5)


def main():
    while True:
        try:
            start_bot()
        except Exception as e:
            print(e)
            print("RETRYING BOT")


if __name__ == "__main__":
    main()
