from flask import Flask, request
from urllib.parse import urljoin
import requests

app = Flask(__name__)

BASE_FILINGRE_NEWS_URL = "https://www.filingre.com/news/"

@app.route('/news/<path:subpath>')
def show_news(subpath):
    filingre_news_url = urljoin(BASE_FILINGRE_NEWS_URL, subpath)
    resp = requests.get(filingre_news_url)
    return resp.content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
