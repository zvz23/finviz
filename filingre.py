from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv
import os

load_dotenv()

FILINGRE_HOME_URL = "https://www.filingre.com/"
FILINGRE_NEWS_URL = "https://www.filingre.com/news"

FILINGRE_EMAIL = os.environ.get('FILINGRE_EMAIL')
FILINGRE_PASSWORD = os.environ.get('FILINGRE_PASSWORD')

def get_news_urls(news_page: Page):
    news_page.bring_to_front()
    news_a_tags = news_page.query_selector_all("div.news-container div.container > div > a")
    news_urls = [i.get_attribute('href') for i in news_a_tags]
    return news_urls

  

def login(news_page: Page):
    while True:
        news_page.bring_to_front()
        news_page.goto(FILINGRE_HOME_URL)
        try:
            login_button = news_page.wait_for_selector("button#login")
            login_button.click()
            print("BUTTON CLICKED")
        except:
            print("ALREADY LOGGED IN")
            return
        try:
            email_input = news_page.wait_for_selector("input[name='email']")
            password_input = news_page.wait_for_selector("input[name='password']")
            submit_button = news_page.wait_for_selector("button[name='submit']")
            email_input.type(FILINGRE_EMAIL)
            password_input.type(FILINGRE_PASSWORD)
            submit_button.click()
            news_page.wait_for_url("https://www.filingre.com/overview")
            news_page.goto(FILINGRE_NEWS_URL)
            break
        except Exception as e:
            print(e)
            print("THERE WAS A PROBLEM LOGGING IN FILINGRE")
    
    

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = b.new_context(no_viewport=True)
        news_page = context.new_page()
        login(news_page)
        input("PRESS ENTER TO CONTINUE..")

if __name__ == '__main__':
    main()
