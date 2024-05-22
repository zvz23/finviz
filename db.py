import sqlite3

class McDonaldsDB:
    def __init__(self, db):
        self.db = db
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()
        self.cursor.row_factory = sqlite3.Row
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def save_news_finviz(self, url: str):
        self.cursor.execute("INSERT OR IGNORE INTO finviz_news(URL) VALUES(?)", (url, ))

    def save_news_many_finviz(self, urls: str):
        self.cursor.executemany("INSERT OR IGNORE INTO finviz_news(URL) VALUES(?)", urls)

    def set_news_exported_finviz(self, url: str):
        self.cursor.execute("UPDATE finviz_news SET IS_EXPORTED=1 WHERE URL=?", (url, ))

    def set_news_exported_many_finviz(self, urls: str):
        self.cursor.executemany("UPDATE finviz_news SET IS_EXPORTED=1 WHERE URL=?", urls)

    def get_news_not_exported_finviz(self):
        self.cursor.execute("SELECT * FROM finviz_news WHERE IS_EXPORTED=0")
        return self.cursor.fetchall()

    def save_news_filingre(self, url: str):
        self.cursor.execute("INSERT OR IGNORE INTO filingre_news(URL) VALUES(?)", (url, ))

    def save_news_many_filingre(self, urls: str):
        self.cursor.executemany("INSERT OR IGNORE INTO filingre_news(URL) VALUES(?)", urls)

    def set_news_exported_filingre(self, url: str):
        self.cursor.execute("UPDATE filingre_news SET IS_EXPORTED=1 WHERE URL=?", (url, ))

    def set_news_exported_many_filingre(self, urls: str):
        self.cursor.executemany("UPDATE filingre_news SET IS_EXPORTED=1 WHERE URL=?", urls)

    def get_news_not_exported_filingre(self):
        self.cursor.execute("SELECT * FROM filingre_news WHERE IS_EXPORTED=0")
        return self.cursor.fetchall()
    
    def save_financial_report_filingre(self, symbol: str, url: str):
        self.cursor.execute("INSERT OR IGNORE INTO filingre_reports(SYMBOL, URL) VALUES(?, ?)", (symbol, name, url, type))
    
    def save_financial_report_many_filingre(self, reports: list):
        self.cursor.executemany("INSERT OR IGNORE INTO filingre_reports(SYMBOL, URL) VALUES(?, ?)", reports)

    def get_financial_report_not_exported_filingre(self):
        self.cursor.execute("SELECT * FROM filingre_reports WHERE IS_EXPORTED=0")
        return self.cursor.fetchall()   
    
    def set_financial_report_exported_filingre(self, id: int):
        self.cursor.execute("UPDATE filingre_reports SET IS_EXPORTED=1 WHERE ID=?", (id, ))

    def set_financial_report_exported_many_filingre(self, ids: list):
        self.cursor.executemany("UPDATE filingre_reports SET IS_EXPORTED=1 WHERE ID=?", ids)
             
    def save_filing_report_filingre(self, symbol: str, url: str):
        self.cursor.execute("INSERT OR IGNORE INTO filingre_filings(SYMBOL, URL) VALUES(?, ?)", (symbol, url))
    
    def save_filing_report_many_filingre(self, reports: list):
        self.cursor.executemany("INSERT OR IGNORE INTO filingre_filings(SYMBOL, URL) VALUES(?, ?)", reports)

    def get_filing_report_not_exported_filingre(self):
        self.cursor.execute("SELECT * FROM filingre_filings WHERE IS_EXPORTED=0")
        return self.cursor.fetchall()   
    
    def set_filing_report_exported_filingre(self, id: int):
        self.cursor.execute("UPDATE filingre_filings SET IS_EXPORTED=1 WHERE ID=?", (id, ))

    def set_filing_report_exported_many_filingre(self, ids: list):
        self.cursor.executemany("UPDATE filingre_filings SET IS_EXPORTED=1 WHERE ID=?", ids) 