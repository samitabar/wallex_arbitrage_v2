import time


from robert import WallexOrderbookCacher
from robert import WallexBalancesCacher
from robert import BinancePricesCacher
from robert import BinanceBalanceCacher
from robert import BinanceInfoCacher
from robert import WallexInfoCacher
from robert import Main
from robert import symbol_constants


def update_cached_info(binance: bool = True, wallex: bool = True):
    if binance is True:
        BinanceInfoCacher()
    if wallex is True:
        WallexInfoCacher()


def main():
    wl_balance_cacher = WallexBalancesCacher(
        token='479628|zzxYQ1MjXELf89ZF45DH1x3lS5YpfQ6Ph0H0g63X',
        sleep_time=1,
        expire_time=3
    )
    print('[Starting] \t wl_balance_cacher')
    wl_balance_cacher.run_thread()
    print('[Finished] \t wl_balance_cacher')

    print('[Starting] \t wl_orderbook_cacher')
    WallexOrderbookCacher(symbols=symbol_constants.WALLEX_SYMBOLS, sleep_time=0, expire_time=2000).run_thread()
    print('[Finished] \t wl_orderbook_cacher')

    print('[Starting] \t binance_prices_cacher')
    BinancePricesCacher(symbols=symbol_constants.ALL_NEEDED_PRICE, sleep_time=0, expire_time=30).run_thread()
    print('[Finished] \t binance_prices_cacher')

    # bi_balance_cacher = BinanceBalanceCacher(
    #     api_key='HE1AWZOSgHxFVX8XJzdwalbVSzAnumcvNaIRAHzoILbc3ygMqytCF9kavsUlLlXY',
    #     api_secret='mSkMjRH0SIIKoZimrh3If4DJPrZYFnlVWjdzEmDK14a213oTL0TqM2epxHhigquU',
    #     sleep_time=0,
    #     expire_time=300000
    # )
    # print('[Starting] \t bi_balance_cacher')
    # bi_balance_cacher.main_main()
    # print('[Finished] \t bi_balance_cacher')

    time.sleep(10)

    print('[Starting] \t Main')
    Main().run()
    print('[Finished] \t Main')


if __name__ == '__main__':
    update_cached_info()
    # print('[Starting] \t main')
    # main()
    # print('[Finished] \t main')
