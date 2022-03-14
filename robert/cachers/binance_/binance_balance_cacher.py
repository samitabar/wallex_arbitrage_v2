import asyncio
from binance import AsyncClient, BinanceSocketManager

import typing as t
from threading import Thread
from multiprocessing import Process


from ... import nice_redis
from ...constants.redis_constants import BINANCE_BALANCES_REDIS_CONSTANTS


from .nice_binance import AsyncNiceBinance


class BinanceBalanceCacher:
    def __init__(
            self, api_key: str, api_secret: str, symbols: t.List = None,
            sleep_time: int = 10, expire_time: int = 10, logger: bool = False
    ):
        self.__api_key = api_key
        self.__api_secret = api_secret

        if symbols is None:
            symbols = []
        self.__symbols = symbols

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time
        self.__logger = logger

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time

        self.__binance_client = AsyncNiceBinance(self.__api_key, self.__api_secret)
        self.__balances_redis = nice_redis.Balances(**BINANCE_BALANCES_REDIS_CONSTANTS.to_dict())

    def init_balance(self):
        loop = asyncio.get_event_loop()
        all_balances = loop.run_until_complete(self.__binance_client.get_balances())

        __balances = {}
        for coin in all_balances.get('balances'):
            __balances[coin.get('asset')] = coin.get('free')
        self.__balances_redis.set_balances(__balances)
        print(__balances)

    async def callback(self, data: t.Dict):
        if data.get('e') == 'outboundAccountPosition':
            balances_arr: list = data.get('B')
            for b in balances_arr:
                asset = b.get('a')
                free = b.get('f')
                self.__balances_redis.update_balances({asset: free})

                print(f"[BALANCES] | {asset=} | {free}")

    async def main(self):
        client = await AsyncClient.create(self.__api_key, self.__api_secret)
        socket_manager = BinanceSocketManager(client)
        ticker_socket = socket_manager.user_socket()
        async with ticker_socket as ts:
            while True:
                res = await ts.recv()
                await self.callback(res)

        await client.close_connection()

        await asyncio.sleep(1)

        await main()

    def main_main(self):
        self.init_balance()
        loop = asyncio.get_event_loop()
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
    BinanceBalanceCacher('', '').main_main()
