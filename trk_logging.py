import sqlite3


class Logger:
    async def log(self, data):
        print(data)

class SqliteLogger(Logger):
    async def __init__(self, file_path: str):
        # Open connection to sqlite db
        self.conn = sqlite3.connect(self.file_path)

    async def log(self, data):
        await super().log(data)
