import typing as t


from ...exceptions import EmptyCacheException

from ...nice_redis import Info
from ...constants.redis_constants import SYMBOLS_INFO_REDIS_CONSTANTS

from wallex import Wallex


__all__ = [
    'WallexInfoCacher'
]


class WallexInfoCacher:
    wallex = Wallex('')
    info_redis = Info(**SYMBOLS_INFO_REDIS_CONSTANTS.to_dict())

    @classmethod
    def __get_exchange_info(cls):
        return cls.wallex.all_market_stats()

    @classmethod
    def __cache_info(cls, info: t.Dict):
        return cls.info_redis.set_info(cls.info_redis.WALLEX_DATA, info)

    @classmethod
    def __read_info(cls):
        return cls.info_redis.read_info(cls.info_redis.BINANCE_DATA)

    @classmethod
    def __cache_all_info(cls):
        info = cls.__get_exchange_info()
        return cls.__cache_info(info)

    @classmethod
    def __read_symbol_data_from_cache(cls, symbol: str) -> t.Dict:
        info = cls.__read_info()
        for i in info['symbols']:
            if i['symbol'] == symbol:
                return i

        raise EmptyCacheException('get_step_size', f'{symbol} not found in cache', info=info)

    @classmethod
    def get_qty_round_point(cls, symbol: str) -> int:
        info = cls.__read_symbol_data_from_cache(symbol)
        _ = info.get('stepSize')
        return int(_)

    @classmethod
    def get_price_round_point(cls, symbol: str) -> int:
        info = cls.__read_symbol_data_from_cache(symbol)
        _ = info.get('tickSize')
        return int(_)

    @classmethod
    def qty_to_dict(cls) -> t.Dict:
        data = {}
        info = cls.__read_info()
        for i in info['symbols']:
            data[i['symbol']] = i['stepSize']

        return data

    @classmethod
    def price_to_dict(cls) -> t.Dict:
        data = {}
        info = cls.__read_info()
        for i in info['symbols']:
            data[i['symbol']] = i['tickSize']

        return data

    def __init__(self):
        self.__cache_all_info()
