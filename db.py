import sqlite3

class FinvizDB:
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
    
    def save_news(self, url: str):
        self.cursor.execute("INSERT OR IGNORE INTO news(URL) VALUES(?)", (url, ))

    def save_news_many(self, urls: str):
        self.cursor.executemany("INSERT OR IGNORE INTO news(URL) VALUES(?)", urls)

    def set_news_exported(self, url: str):
        self.cursor.execute("UPDATE news SET IS_EXPORTED=1 WHERE URL=?", (url, ))

    def set_news_exported_many(self, urls: str):
        self.cursor.executemany("UPDATE news SET IS_EXPORTED=1 WHERE URL=?", urls)

    def get_news_not_exported(self):
        self.cursor.execute("SELECT * FROM news WHERE IS_EXPORTED=0")
        return self.cursor.fetchall()