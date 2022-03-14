from typing import List

import asyncio
from binance import AsyncClient, BinanceSocketManager

import typing as t
from threading import Thread
from multiprocessing import Process


from ... import nice_redis
from ...constants.redis_constants import BINANCE_PRICES_REDIS_CONSTANTS


from .nice_binance import AsyncNiceBinance


class BinancePricesCacher:
    def __init__(self, symbols: t.List = None, sleep_time: int = 10, expire_time: int = 10, logger: bool = False):
        if symbols is None:
            symbols = []
        self.__symbols = symbols

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time
        self.__logger = logger

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time

        self.__binance_client = AsyncNiceBinance()
        self.__prices_redis = nice_redis.BinancePrices(**BINANCE_PRICES_REDIS_CONSTANTS.to_dict())

    async def callback(self, data: List):
        for ticker in data:
            event = ticker.get('e')
            if event == '24hrTicker':
                symbol = ticker.get('s')
                if self.__symbols is not None and len(self.__symbols) > 0:
                    if symbol.upper() in self.__symbols:
                        pass
                    else:
                        continue

                price = ticker.get('c')
                self.__prices_redis.cache__prices(symbol, price, self.__expire_time)

                if self.__logger:
                    print(f"[PRICES] \t {symbol=} \t {price}")

    async def main(self):
        client = await AsyncClient.create()
        socket_manager = BinanceSocketManager(client)
        ticker_socket = socket_manager.ticker_socket()
        async with ticker_socket as ts:
            while True:
                res = await ts.recv()
                await self.callback(res)

        await client.close_connection()

        await asyncio.sleep(1)

        await main()

    def main_main(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main())

    def __main(self):
        self.main_main()

    def run(self):
        self.__main()

    def run_thread(self):
        thread = Thread(target=self.run)
        thread.start()
        return thread

    def run_process(self):
        process = Process(target=self.run)
        process.start()
        return process


if __name__ == "__main__":
    BinancePricesCacher().run_thread()
