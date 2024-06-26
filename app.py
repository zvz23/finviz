from dotenv import load_dotenv
from discord.ext import tasks
from db import McDonaldsDB
from formatters import *
from urllib.parse import urlparse, urljoin
import discord
import os
import logging
import json
import asyncio


load_dotenv(override=True)

handler = logging.FileHandler(filename='app.log', encoding='utf-8', mode='w')
logger = logging.getLogger('discord')

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_NAME = 'mcdonalds.db'
TICKERS_CHANNEL = 1241211391952551969
FINVIZ_NEWS_CHANEL = 1241211355449655389
FUTURES_CHANNEL = 1241237696505188466
REPORTS_CHANNEL = 1242120229920837642
FILINGRE_NEWS_CHANNEL = 1243213152707940372

MCCCDONALDS_BASE_URL = "http://67.211.216.97:5000/news/"



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def replace_filingre_news_url(news_url: str):
    parsed_news_url = urlparse(news_url)
    news_path = parsed_news_url.path
    return urljoin(MCCCDONALDS_BASE_URL, news_path)

def get_tickers_finviz():
    tickers = None
    with open('tickers_finviz.json', 'r') as f:
        tickers = json.load(f)
    return tickers

def get_futures_finviz():
    futures = None
    with open('futures_finviz.json', 'r') as f:
        futures = json.load(f)
    return futures

def get_reports_filingre():
    with McDonaldsDB(DB_NAME) as conn:
        return conn.get_report_not_exported_filingre()

@tasks.loop(seconds=10.0)
async def send_news():
    not_exported_finviz_news = None
    with McDonaldsDB(DB_NAME) as conn:
        not_exported_finviz_news = conn.get_news_not_exported_finviz()
    if not_exported_finviz_news:
        channel = client.get_channel(FINVIZ_NEWS_CHANEL)
        news_urls = [i['URL'] for i in not_exported_finviz_news]
        for news_url in news_urls:
            await channel.send(news_url)
        with McDonaldsDB(DB_NAME) as conn:
            conn.set_news_exported_many_finviz([[i] for i in news_urls])
        logger.info("SENT %s FINVIZ NEWS", len(news_urls))

    not_exported_filingre_news = None
    with McDonaldsDB(DB_NAME) as conn:
        not_exported_filingre_news = conn.get_news_not_exported_filingre()
    if not_exported_filingre_news:
        channel = client.get_channel(FILINGRE_NEWS_CHANNEL)
        news_urls = [i['URL'] for i in not_exported_filingre_news]
        for news_url in news_urls:
            if "filingre.com/news/" in news_url:
                new_news_url = replace_filingre_news_url(news_url)
                await channel.send(new_news_url)
            else:
                await channel.send(news_url)
    if not_exported_filingre_news:
        with McDonaldsDB(DB_NAME) as conn:
            conn.set_news_exported_many_filingre([[i] for i in news_urls])
        logger.info("SENT %s FILINGRE NEWS", len(news_urls))

@tasks.loop(minutes=10.0)
async def send_tickers_and_futures_and_reports():
    tickers_channel = client.get_channel(TICKERS_CHANNEL)
    futures_channel = client.get_channel(FUTURES_CHANNEL)
    reports_channel = client.get_channel(REPORTS_CHANNEL)
    tickers = get_tickers_finviz()
    futures = get_futures_finviz()
    filingre_reports = get_reports_filingre()
    tickers_tables = format_tickers_finviz_ascii(tickers)
    futures_tables = format_futures_finviz_ascii(futures)
    reports_tables = format_reports_filingre(filingre_reports)
    for table in tickers_tables:
        await tickers_channel.send(f"```\n{table}\n```")
    for table in futures_tables:
        await futures_channel.send(f"```\n{table}\n```")
    for table in reports_tables:
        await reports_channel.send(table)
        with McDonaldsDB(DB_NAME) as conn:
            conn.set_report_exported_many_filingre([[i['ID']] for i in filingre_reports])
    
    logger.info("SENT TICKERS AND REPORTS")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await asyncio.gather(send_news.start(), send_tickers_and_futures_and_reports.start())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(BOT_TOKEN, log_handler=handler)
