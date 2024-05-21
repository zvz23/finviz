from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv
from db import McDonaldsDB
from urllib.parse import urljoin
import os
import time

load_dotenv()

FILINGRE_HOME_URL = "https://www.filingre.com/"
FILINGRE_NEWS_URL = "https://www.filingre.com/news"
FILINGRE_REPORTS_URL = "https://www.filingre.com/sec-financial-reports"

FILINGRE_EMAIL = os.environ.get('FILINGRE_EMAIL')
FILINGRE_PASSWORD = os.environ.get('FILINGRE_PASSWORD')

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
        'financial_reports': [],
        'filings_reports': []
    }
    for report_sel in financial_reports_sels:
        financial_report = {}
        financial_report['symbol'] = report_sel.query_selector("div.list-symbol > h4").inner_text().strip()
        financial_report['name'] = report_sel.query_selector("h4.list-name").inner_text().strip()
        financial_report['report_type'] = report_sel.query_selector("h4[ng-if='data.form']").inner_text().strip()
        financial_report['report_url'] = report_sel.query_selector(":scope > a").get_attribute('href')
        reports["financial_reports"].append(financial_report)

    sec_filings_sels = reports_page.query_selector_all("#financials-container-sec div.container > div")
    for filing_sel in sec_filings_sels:
        filing = {}
        filing['symbol'] = filing_sel.query_selector("div.list-symbol h4").inner_text().strip()
        filing['filing_url'] = filing_sel.eval_on_selector(":scope > a", "node => node.href")
        reports['filings_reports'].append(filing)

    return reports



def login(news_page: Page):
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
    
    

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = b.new_context(no_viewport=True)
        filingre_news_page = context.new_page()
        filingre_reports_page = context.new_page()
        login(filingre_news_page)
        filingre_news_page.goto(FILINGRE_NEWS_URL)
        filingre_reports_page.bring_to_front()
        filingre_reports_page.goto(FILINGRE_REPORTS_URL)
        news_urls = get_news_filingsre(filingre_news_page)
        reports = get_reports_filingre(filingre_reports_page)
        news_urls = [[i] for i in news_urls]
        financial_reports = reports['financial']
        filing_reports = reports['filings']
        financial_reports = [[i['symbol'], i['name'], i['report_url'], i['report_type']] for i in financial_reports]
        filing_reports = [[i['symbol'], i['filing_url']] for i in filing_reports]
        with McDonaldsDB('mcdonalds.db') as conn:
            conn.save_news_many_filingre(news_urls)
            conn.save_report_many_filingre(financial_reports)
            conn.save_filing_many_filingre(filing_reports)

if __name__ == '__main__':
    main()
