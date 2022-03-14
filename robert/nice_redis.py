import typing as t

import json
import redis


from .exceptions import *


__all__ = [
    'Orderbook',
    'Balances',
]


class BaseRedis:
    def __init__(self, host: str, port: int, db: int, password: str = None) -> None:
        self.__redis_conn = redis.StrictRedis(
            host=host, port=port, db=db, password=password, decode_responses=True, connection_pool=False
        )

    def _base_cache_data(self, key: str, data: str, expire: int = None) -> None:
        self.__redis_conn.set(key, data, ex=expire)

    def _base_read_data(self, key: str) -> t.Union[str, None]:
        data = self.__redis_conn.get(key)

        if data is None:
            return None
        else:
            return data

    def _read_all(self) -> t.List:
        return self.__redis_conn.keys()


class Orderbook(BaseRedis):
    def __init__(self, host: str, port: int, db: int, password: str = None):
        super().__init__(host, port, db, password)

    def cache__orderbook(self, symbol: str, orderbook: t.Dict, expire: int = None) -> None:
        self._base_cache_data(symbol, json.dumps(orderbook), expire)

    def read__orderbook(self, symbol: str) -> t.Dict:
        orderbook = self._base_read_data(symbol)

        if orderbook is None:
            raise EmptyCacheException('Orderbook', f'No Cache Found For {symbol}', symbol)

        return json.loads(orderbook)


class BinancePrices(BaseRedis):
    def __init__(self, host: str, port: int, db: int, password: str = None):
        super().__init__(host, port, db, password)

    def cache__prices(self, symbol: str, price: str, expire: int = None) -> None:
        self._base_cache_data(symbol, str(price), expire)

    def read__prices(self, symbol: str) -> float:
        symbol = symbol.upper()
        if symbol == 'USDTUSDT':
            return 1

        price = self._base_read_data(symbol)

        if price is None:
            raise EmptyCacheException('BinancePrices', f'No Cache Found For {symbol}', symbol)

        return float(price)


class Balances(BaseRedis):
    def __init__(self, host: str, port: int, db: int, password: str = None):
        self.BALANCES = 'BALANCES'
        super().__init__(host, port, db, password)

    def set_balances(self, balances: t.Dict, expire_time: int = 24 * 60 * 60) -> None:
        self._base_cache_data(self.BALANCES, json.dumps(balances), expire_time)

    def update_balances(self, balances: t.Dict) -> None:
        get_balance = self._base_read_data(self.BALANCES)
        balances_dict = json.loads(get_balance) if get_balance is not None else {}
        balances_dict.update(balances)
        self.set_balances(balances_dict)

    def read_all_balances(self) -> t.Union[t.Dict, None]:
        all_balances = self._base_read_data(self.BALANCES)
        if all_balances is None:
            raise EmptyCacheException('Balances', f'No Cache Found read_all_balances')
        return json.loads(all_balances)

    def read_balance(self, coin: str):
        balances = self.read_all_balances()
        if balances is None:
            raise EmptyCacheException('Balances', f'No Cache Found For {coin}', coin)
        return balances.get(coin)
