from dotenv import load_dotenv
from discord.ext import tasks
from db import McDonaldsDB
from formatters import *
import discord
import os
import logging
import json
import asyncio


load_dotenv()

handler = logging.FileHandler(filename='app.log', encoding='utf-8', mode='w')
logger = logging.getLogger('discord')

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_NAME = 'finviz.db'
TICKERS_CHANNEL = 1241211391952551969
NEWS_CHANEL = 1241211355449655389
FUTURES_CHANNEL = 1241237696505188466

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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


@tasks.loop(seconds=10.0)
async def send_news_finviz():
    not_exported_news = None
    with McDonaldsDB(DB_NAME) as conn:
        not_exported_news = conn.get_news_not_exported_finviz()
    if not_exported_news:
        channel = client.get_channel(NEWS_CHANEL)
        news_urls = [i['URL'] for i in not_exported_news]
        for news_url in news_urls:
            await channel.send(news_url)
        with McDonaldsDB(DB_NAME) as conn:
            conn.set_news_exported_many_finviz([[i] for i in news_urls])
        logger.info("SENT %s NEWS", len(news_urls))

@tasks.loop(minutes=10.0)
async def send_tickers_and_futures():
    tickers_channel = client.get_channel(TICKERS_CHANNEL)
    futures_channel = client.get_channel(FUTURES_CHANNEL)
    tickers = get_tickers()
    futures = get_futures()
    tickers_tables = format_tickers_ascii(tickers)
    futures_tables = format_futures_ascii(futures)
    for table in tickers_tables:
        await tickers_channel.send(f"```\n{table}\n```")
    for table in futures_tables:
        await futures_channel.send(f"```\n{table}\n```")
    logger.info("SENT TICKERS")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await asyncio.gather([send_news_finviz.start(), send_tickers_and_futures.start()])

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(BOT_TOKEN, log_handler=handler)
