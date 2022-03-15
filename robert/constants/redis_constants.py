from dotenv import load_dotenv
import os


load_dotenv(dotenv_path='../../.env')


class RedisConstants:
    def __init__(self, db: int, host: str = os.environ.get('REDIS_HOST') or 'localhost',
                 port: int = os.environ.get('REDIS_PORT') or 6379):
        self.host = host
        self.port = port
        self.db = db

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db
        }

    def from_dict(self, d: dict) -> 'RedisConstants':
        self.host = d['host']
        self.port = d['port']
        self.db = d['db']

        return self


BINANCE_PRICES_REDIS_CONSTANTS = RedisConstants(db=0)
WALLEX_ORDERBOOK_REDIS_CONSTANTS = RedisConstants(db=1)
BINANCE_BALANCES_REDIS_CONSTANTS = RedisConstants(db=3)
WALLEX_BALANCES_REDIS_CONSTANTS = RedisConstants(db=4)
SYMBOLS_INFO_REDIS_CONSTANTS = RedisConstants(db=5)
