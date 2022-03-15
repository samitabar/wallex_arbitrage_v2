import typing as t


from ...exceptions import EmptyCacheException

from ...nice_redis import Info
from ...constants.redis_constants import SYMBOLS_INFO_REDIS_CONSTANTS

from .nice_binance import SyncBinance


__all__ = [
    'BinanceInfoCacher'
]


class BinanceInfoCacher:
    binance = SyncBinance()
    info_redis = Info(**SYMBOLS_INFO_REDIS_CONSTANTS.to_dict())

    @classmethod
    def get_exchange_info(cls):
        return cls.binance.get_exchange_info()

    @classmethod
    def cache_info(cls, info: t.Dict):
        return cls.info_redis.set_info(cls.info_redis.BINANCE_DATA, info)

    @classmethod
    def read_info(cls):
        return cls.info_redis.read_info(cls.info_redis.BINANCE_DATA)

    @classmethod
    def _cache_all_info(cls):
        info = cls.get_exchange_info()
        return cls.cache_info(info)

    @classmethod
    def _read_step_size_from_cache(cls, symbol: str) -> str:
        info = cls.read_info()
        for i in info['symbols']:
            if i['symbol'] == symbol:
                return i['filters'][2]['stepSize']

        raise EmptyCacheException('get_step_size', f'{symbol} not found in cache', info=info)

    @classmethod
    def get_step_size(cls, symbol: str) -> int:
        step_size = cls._read_step_size_from_cache(symbol)

        one_place = step_size.find('1')

        if one_place == 0:
            _ = one_place
        else:
            _ = one_place - 1

        return int(_)

    def __init__(self):
        self._cache_all_info()
