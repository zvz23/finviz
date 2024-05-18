from dotenv import load_dotenv
from discord.ext import tasks
from db import FinvizDB
from prettytable import PrettyTable
from table2ascii import table2ascii as t2a, PresetStyle
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
TICKERS_CHANNEL = 1240989466152271985
NEWS_CHANEL = 1240637900299702312

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_tickers():
    tickers = None
    with open('tickers.json', 'r') as f:
        tickers = json.load(f)
    return tickers

def format_tickers(tickers_obj: dict):
    tables = []
    tickers = tickers_obj['tickers']
    tickers_only = tickers_obj['tickers_only']
    tickers_table = PrettyTable()
    tickers_only_table = PrettyTable()
    tickers_table.field_names = ["Ticker", "Last", "Change", "Volume", "Signal"]
    tickers_only_table.field_names = ["Tickers", "Signal"]
    mid_index_tickers = len(tickers) // 2
    mid_index_tickers_only = len(tickers_only) // 2

    tickers_rows_one = [[i['ticker'], i['last'], i['change'], i['volume'], i['signal']] for i in tickers[:mid_index_tickers]]
    tickers_rows_two = [[i['ticker'], i['last'], i['change'], i['volume'], i['signal']] for i in tickers[mid_index_tickers:]]
    tickers_table.add_rows(tickers_rows_one)
    tables.append(tickers_table.get_string())
    tickers_table.clear_rows()
    tickers_table.add_rows(tickers_rows_two)
    tables.append(tickers_table.get_string())

    tickers_only_rows_one = [[' '.join(i['tickers']), i['signal']] for i in tickers_only[:mid_index_tickers_only]]
    tickers_only_rows_two = [[' '.join(i['tickers']), i['signal']] for i in tickers_only[mid_index_tickers_only:]]
    tickers_only_table.add_rows(tickers_only_rows_one)
    tables.append(tickers_only_table.get_string())
    tickers_only_table.clear_rows()
    tickers_only_table.add_rows(tickers_only_rows_two)
    tables.append(tickers_only_table.get_string())


    return tables


def format_tickers_ascii(tickers_obj: dict):
    tables = []
    tickers = tickers_obj['tickers']
    tickers_only = tickers_obj['tickers_only']
    mid_index_tickers = len(tickers) // 2
    mid_index_tickers_only = len(tickers_only) // 2
    tickers_rows_one = [[i['ticker'], i['last'], i['change'], i['volume'], i['signal']] for i in tickers[:mid_index_tickers]]
    tickers_rows_two = [[i['ticker'], i['last'], i['change'], i['volume'], i['signal']] for i in tickers[mid_index_tickers:]]
    tickers_only_rows_one = [[' '.join(i['tickers']), i['signal']] for i in tickers_only[:mid_index_tickers_only]]
    tickers_only_rows_two = [[' '.join(i['tickers']), i['signal']] for i in tickers_only[mid_index_tickers_only:]]
    
    tables.append(t2a(
        header=["Ticker", "Last", "Change", "Volume", "Signal"],
        body=tickers_rows_one,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Ticker", "Last", "Change", "Volume", "Signal"],
        body=tickers_rows_two,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Tickers", "Signal"],
        body=tickers_only_rows_one,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Tickers", "Signal"],
        body=tickers_only_rows_two,
        style=PresetStyle.thin_compact
    ))
    return tables

@tasks.loop(seconds=10.0)
async def send_news():
    not_exported_news = None
    with FinvizDB(DB_NAME) as conn:
        not_exported_news = conn.get_news_not_exported()
    if not_exported_news:
        channel = client.get_channel(NEWS_CHANEL)
        news_urls = [i['URL'] for i in not_exported_news]
        for news_url in news_urls:
            await channel.send(news_url)
        with FinvizDB(DB_NAME) as conn:
            conn.set_news_exported_many([[i] for i in news_urls])
        logger.info("SENT %s NEWS", len(news_urls))

@tasks.loop(minutes=10.0)
async def send_tickers():
    tickers_channel = client.get_channel(TICKERS_CHANNEL)
    tickers = get_tickers()
    tickers_tables = format_tickers_ascii(tickers)
    for ticker_table in tickers_tables:
        await tickers_channel.send(f"```\n{ticker_table}\n```")
    logger.info("SENT TICKERS")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await asyncio.gather([send_news.start(), send_tickers.start()])

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(BOT_TOKEN, log_handler=handler)
