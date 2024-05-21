from prettytable import PrettyTable
from table2ascii import table2ascii as t2a, PresetStyle

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



def format_futures_ascii(futures: list):
    tables = []
    n = len(futures)
    # Calculate the size of each part
    part_size = n // 4
    remainder = n % 4

    futures_row_one = [[i['ticker'], i['price'], i['high'], i['high_gain'], i['low'], i['low_gain']] for i in futures[:part_size]]
    futures_row_two = [[i['ticker'], i['price'], i['high'], i['high_gain'], i['low'], i['low_gain']] for i in futures[part_size:part_size * 2]]
    futures_row_three = [[i['ticker'], i['price'], i['high'], i['high_gain'], i['low'], i['low_gain']] for i in futures[part_size * 2:part_size * 3]]
    futures_row_fourth = [[i['ticker'], i['price'], i['high'], i['high_gain'], i['low'], i['low_gain']] for i in futures[part_size * 3:]]
    tables.append(t2a(
        header=["Ticker", "Price", "High", "Gain", "Low", "Gain"],
        body=futures_row_one,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Ticker", "Price", "High", "Gain", "Low", "Gain"],
        body=futures_row_two,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Ticker", "Price", "High", "Gain", "Low", "Gain"],
        body=futures_row_three,
        style=PresetStyle.thin_compact
    ))
    tables.append(t2a(
        header=["Ticker", "Price", "High", "Gain", "Low", "Gain"],
        body=futures_row_fourth,
        style=PresetStyle.thin_compact
    ))
    return tables