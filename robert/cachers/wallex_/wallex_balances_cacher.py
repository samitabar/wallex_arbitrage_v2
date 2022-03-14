import typing as t
from traceback import print_exc as pe
from threading import Thread
from multiprocessing import Process


import time
from concurrent.futures import ThreadPoolExecutor
from wallex import Wallex


from ... import nice_redis
from ...constants.redis_constants import WALLEX_BALANCES_REDIS_CONSTANTS


class WallexBalancesCacher:
    def __init__(self, token: t.Text, sleep_time: int = 10, expire_time: int = 10, logger: bool = False):
        self.__token = token

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time
        self.__logger = logger

        self.__sleep_time = sleep_time
        self.__expire_time = expire_time

        self.__wallex = Wallex(self.__token)
        self.__balances_redis = nice_redis.Balances(**WALLEX_BALANCES_REDIS_CONSTANTS.to_dict())

        self.__executor = ThreadPoolExecutor(max_workers=32)

    def _cache_balances(self):
        if self.__logger is True:
            print(f'Wallex | cache balances ')

        balances = self.__wallex.all_balances()
        self.__balances_redis.set_balances(balances, self.__expire_time)

    def __main(self):
        self._cache_balances()

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
    WallexBalancesCacher('479628|zzxYQ1MjXELf89ZF45DH1x3lS5YpfQ6Ph0H0g63X').run_process()
