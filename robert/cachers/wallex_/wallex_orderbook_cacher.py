import typing as t
from traceback import print_exc as pe
from threading import Thread
from multiprocessing import Process


import time
from concurrent.futures import ThreadPoolExecutor
from wallex import Wallex


from ... import nice_redis
from ...constants.redis_constants import WALLEX_ORDERBOOK_REDIS_CONSTANTS


class WallexOrderbookCacher:
    def __init__(self, symbols: t.List = None, sleep_time: int = 10, expire_time: int = 10, logger: bool = False):
        if symbols is None:
            symbols = []
        self.__symbols = symbols

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time
        self.__logger = logger

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time

        self.__wallex = Wallex('')
        self.__orderbook_redis = nice_redis.Orderbook(**WALLEX_ORDERBOOK_REDIS_CONSTANTS.to_dict())

        self.__executor = ThreadPoolExecutor(max_workers=32)

    def _cache_orderbook(self, symbol):
        if self.__logger is True:
            print(f'Wallex | cache orderbook -> {symbol}')

        orderbook = self.__wallex.order_book(symbol)
        self.__orderbook_redis.cache__orderbook(symbol, orderbook, self.__expire_time)

    def __main(self):
        submits = [self.__executor.submit(self._cache_orderbook, symbol) for symbol in self.__symbols]
        [submit.result() for submit in submits]

    def run(self):
        while True:
            try:
                self.__main()
            except Exception as e:
                print(f'[ERROR] -> main() -> Exception -> \n{e}\n{pe()}')
                continue

            time.sleep(self.__sleep_time)

    def run_thread(self):
        thread = Thread(target=self.run)
        thread.start()
        return thread

    def run_process(self):
        process = Process(target=self.run)
        process.start()
        return process


if __name__ == '__main__':
    WallexOrderbookCacher().run_process()
