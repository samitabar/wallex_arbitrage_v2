import typing as t
import time

from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from traceback import print_exc as pe

from wallex import Wallex
from binance import Client


from .. import nice_redis

from ..constants.redis_constants import BINANCE_PRICES_REDIS_CONSTANTS
from ..constants.redis_constants import WALLEX_ORDERBOOK_REDIS_CONSTANTS
from ..constants.redis_constants import BINANCE_BALANCES_REDIS_CONSTANTS
from ..constants.redis_constants import WALLEX_BALANCES_REDIS_CONSTANTS

from ..helpers import offline as offline_helper
from ..helpers import online as online_helper
from ..helpers.models import WallexOrder, BinancePaths

from ..exceptions import DeciderException

from ..cachers import WallexInfoCacher, BinanceInfoCacher


class AfterOrder:
    def __init__(self, wl: Wallex, order_results: t.List, run_thread: bool = False) -> None:
        self.__wl = wl

        if run_thread:
            Thread(
                target=self.__main__,
                args=(order_results,),
            ).start()
        else:
            self.__main__(order_results)

    def __main__(self, order_results) -> None:
        active_orders = self.order_decider(order_results)

        if active_orders and len(active_orders) > 0:
            self.order_decider(active_orders)

    @staticmethod
    def order_decider(order_results: t.List) -> t.List:
        _ = []

        for order in order_results:
            if order.get('active'):
                _.append(order)

        return _

    def order_marketer(self, order_results: t.List[t.Dict[t.Text, t.Any]]) -> None:
        m = 60
        time.sleep(5 * m)

        for order in order_results:
            recheck = self.__wl.get_order_by_id(
                str(order.get('clientOrderId')),
            )

            if recheck.get('active'):
                online_helper.canceler(
                    self.__wl,
                    order.get('clientOrderId'),
                )

                amount = offline_helper.calculate_remaining_amount(order)

                try:
                    market = self.__wl.create_order(
                        symbol=recheck.get('symbol').lower(),
                        side=recheck.get('side').lower(),
                        type_='market',
                        quantity=str(amount),
                        price='1',
                    )

                except Exception as exx:
                    print(exx)
                    return

                try:
                    loss = offline_helper.calculate_loss(recheck, market)
                except Exception as exx:
                    print(exx)


class AfterArbitrageHandler:
    def __init__(
            self, wl: Wallex, binance: Client,
            order_results: t.List[t.Union[t.Dict, None]], revert_on_exception: bool = True
    ) -> None:
        self.__wl = wl
        self.__binance = binance
        self.order_results = order_results
        self.revert_on_exception = revert_on_exception

        self.__BINANCE_EXCHANGE = 'wallex'
        self.__WALLEX_EXCHANGE = 'wallex'

        self.__SELL = 'sell'
        self.__BUY = 'buy'

        self.__main__()

    def _cancel_active(self, order: t.Dict) -> t.Union[t.Dict, bool]:
        if order.get('active'):
            _ = online_helper.canceler(
                self.__wl,
                order.get('clientOrderId'),
            )
            return _

        return False

    def _revert_side(self, order: t.Dict) -> t.Text:
        if order.get('side').lower() == self.__SELL:
            return self.__BUY
        elif order.get('side').lower() == self.__BUY:
            return self.__SELL

    def _get_exchange_from_order(self, order: t.Dict) -> t.Text:
        if 'timeInForce' in order.keys():
            return self.__BINANCE_EXCHANGE
        else:
            return self.__WALLEX_EXCHANGE

    def revert_wallex_order(self, order: t.Dict) -> None:
        self._cancel_active(order)

        reverted_side = self._revert_side(order)

        market = self.__wl.create_order(
            symbol=order.get('symbol').lower(),
            side=reverted_side,
            type_='market',
            quantity=str(offline_helper.calculate_remaining_amount(order)),
            price='1',
        )

    def _revert_binance_order(self, order: t.Dict) -> t.Dict:
        reverted_side = self._revert_side(order)

        if reverted_side == self.__SELL:
            _ = self.__binance.order_market_sell(
                symbol=order.get('symbol').lower(),
                quantity=str(order.get('executedQty')),
            )
        elif reverted_side == self.__BUY:
            _ = self.__binance.order_market_buy(
                symbol=order.get('symbol').lower(),
                quantity=str(order.get('executedQty')),
            )
        else:
            raise Exception('Unknown side')

        return _

    def _revert_order(self, order: t.Dict) -> None:
        exchange = self._get_exchange_from_order(order)

        if exchange == self.__BINANCE_EXCHANGE:
            self._revert_binance_order(order)
        else:
            self.revert_wallex_order(order)

    def __main__(self) -> None:
        if self.revert_on_exception:
            if not all(self.order_results):
                for order in self.order_results:
                    if order is not None:
                        self._revert_order(order)
            else:
                print('All executed')

        else:
            AfterOrder(self.__wl, self.order_results)


class Main:
    def __init__(self, wallex_token: str, binance_api_key: str, binance_api_secret: str,
                 symbols: t.List, fee: t.Union[float, int] = 0.01,
                 threaded_place_order: bool = False, revert_on_exception: bool = False,
                 add_coin_after_time: int = 60, max_workers: int = 10,
                 sleep_time: int = 2, expire_time: int = 5, logger: bool = False) -> None:

        self.__binance_price_redis = nice_redis.BinancePrices(**BINANCE_PRICES_REDIS_CONSTANTS.to_dict())
        self.__wallex_orderbook_redis = nice_redis.Orderbook(**WALLEX_ORDERBOOK_REDIS_CONSTANTS.to_dict())

        self.__binance_balances_redis = nice_redis.Balances(**BINANCE_BALANCES_REDIS_CONSTANTS.to_dict())
        self.__wallex_balances_redis = nice_redis.Balances(**WALLEX_BALANCES_REDIS_CONSTANTS.to_dict())

        self.__wallex_token = wallex_token
        self.__binance_api_key = binance_api_key
        self.__binance_api_secret = binance_api_secret

        self.__wl = Wallex(self.__wallex_token)
        self.__binance = Client(self.__binance_api_key, self.__binance_api_secret)

        self.__symbols = symbols
        self.__fee = fee
        self.__threaded_place_order = threaded_place_order
        self.__revert_on_exception = revert_on_exception
        self.__add_coin_after_time = add_coin_after_time
        self.__max_workers = max_workers
        self.__sleep_time = sleep_time
        self.__expire_time = expire_time
        self.__logger = logger

    def _get_executor(self, max_workers: int = None, thread_name_prefix: str = '') -> ThreadPoolExecutor:
        if max_workers is None:
            max_workers = self.__max_workers
        return ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix)

    def _handle_insufficient_funds(self, symbol: str, exchange: str) -> None:
        coin = offline_helper.coin_name(symbol).upper() + 'TMN'

        if (exchange.lower() == 'wallex' and coin != 'USDTTMN ') or \
                (exchange.lower() == 'wallex' and coin != 'TMNTMN'):
            if coin in self.__symbols:
                self.__symbols.remove(coin.upper() + "TMN")

            time.sleep(self.__sleep_time)

            if coin not in self.__symbols:
                self.__symbols.append(coin.upper() + "TMN")

    def main(self) -> bool:
        buys = {}
        sells = {}

        for symbol in self.__symbols.copy():
            orderbook = self.__wallex_orderbook_redis.read__orderbook(symbol)
            orderbook = offline_helper.filter_orderbook(orderbook, 300000)
            coin_name = offline_helper.coin_name(symbol) + 'USDT'
            binance_price = self.__binance_price_redis.read__prices(coin_name)
            first_buy = orderbook.get('bid')[0]
            first_sell = orderbook.get('ask')[0]

            data = {
                'symbol': symbol,
                'binance_price': binance_price,
                'usdt_price': float(first_buy.get('price')) / float(binance_price),
                'orderbook': orderbook.get('bid')[0],
            }
            buys.update({symbol: data})
            data = {
                'symbol': symbol,
                'binance_price': binance_price,
                'usdt_price': float(first_sell.get('price')) / float(binance_price),
                'orderbook': orderbook.get('ask')[0],
            }
            sells.update({symbol: data})

        # sort buys by wallex price
        buys = dict(sorted(buys.items(), key=lambda x: x[1].get('usdt_price'), reverse=True))
        sells = dict(sorted(sells.items(), key=lambda x: x[1].get('usdt_price')))

        highest_buy_data = buys.get(list(buys.keys())[0])
        lowest_sell_data = sells.get(list(sells.keys())[0])

        highest_buy_order = WallexOrder(
            order=highest_buy_data.get('orderbook'),
            symbol=highest_buy_data.get('symbol'),
            binance_price=highest_buy_data.get('binance_price'),
            tether_price=highest_buy_data.get('usdt_price'),
        )
        lowest_sell_order = WallexOrder(
            order=lowest_sell_data.get('orderbook'),
            symbol=lowest_sell_data.get('symbol'),
            binance_price=lowest_sell_data.get('binance_price'),
            tether_price=lowest_sell_data.get('usdt_price'),
        )

        high_to_low_percentage = offline_helper.calculate_gap_percent(
            highest_buy_order.tether_price, lowest_sell_order.tether_price
        )
        arbitrage_path = offline_helper.path_decider(lowest_sell_order.symbol, highest_buy_order.symbol)

        if arbitrage_path == BinancePaths.BuyBuySell:
            if high_to_low_percentage >= self.__fee:
                return self._buy_buy_sell_arbitrage(highest_buy_order, lowest_sell_order)
            return False

        elif arbitrage_path == BinancePaths.BuySellSell:
            if high_to_low_percentage >= self.__fee:
                return self._buy_sell_sell_arbitrage(highest_buy_order, lowest_sell_order)
            return False

        elif arbitrage_path == BinancePaths.TwoChain:
            if high_to_low_percentage >= self.__fee * 2:
                return self._two_chain_arbitrage(highest_buy_order, lowest_sell_order)
            return False

        elif arbitrage_path == BinancePaths.SameCoin:
            return self._same_coin_arbitrage()

        else:
            raise DeciderException('Main', f'Wrong Arbitrage Path -> {arbitrage_path}')

    def _buy_buy_sell_arbitrage(
            self,
            highest_buy_order: WallexOrder,
            lowest_sell_order: WallexOrder,
            threaded: bool = False,
            revert_on_exception: bool = False
    ) -> bool:
        """
        Buy highest buy order and sell lowest sell order

        :param highest_buy_order: Highest buy order data
        :type highest_buy_order: WallexOrder

        :param lowest_sell_order: Lowest sell order data
        :type lowest_sell_order: WallexOrder

        :return: True if arbitrage is possible
        :rtype: bool
        """

        binance_symbol, binance_src, binance_dst, binance_src_price, binance_dst_price, binance_rate = \
            offline_helper.find_binance_symbol_binance_src_binance_dst_src_price_dst_price_rate(
                lowest_sell_order,
                highest_buy_order,
            )

        wallex_tmn_balance, wallex_coin_balance, binance_coin_balance = self._find_balances(
            wallex_coin=offline_helper.coin_name(highest_buy_order.symbol),
            binance_coin_one=binance_dst.upper(),
        )

        base_lowest_quantity_in_usdt = min(highest_buy_order.volume_in_usdt, lowest_sell_order.volume_in_usdt)
        highest_buy_quantity_for_arbitrage = base_lowest_quantity_in_usdt / highest_buy_order.binance_price
        lowest_sell_quantity_for_arbitrage = base_lowest_quantity_in_usdt / lowest_sell_order.binance_price

        # print all data
        print(f'{highest_buy_order=} \n{lowest_sell_order=} \n{binance_symbol=} \n{binance_src=} \n{binance_dst=} \n'
              f'{binance_src_price=} \n{binance_dst_price=} \n{binance_rate=} \n'
              f'{wallex_tmn_balance=} \n{binance_coin_balance=} \n{wallex_coin_balance=} \n'
              f'{highest_buy_quantity_for_arbitrage=} \n{lowest_sell_quantity_for_arbitrage=} \n')
        print(f'----------------------------------')

        # Check for balances

        if wallex_tmn_balance < lowest_sell_quantity_for_arbitrage * lowest_sell_order.price:
            Thread(
                target=self._handle_insufficient_funds,
                args=('TMN', 'wallex')
            ).start()
            return False

        if binance_coin_balance < highest_buy_quantity_for_arbitrage * binance_rate:
            Thread(
                target=self._handle_insufficient_funds,
                args=(binance_dst.upper(), 'wallex')
            ).start()
            return False

        if wallex_coin_balance < highest_buy_quantity_for_arbitrage:
            Thread(
                target=self._handle_insufficient_funds,
                args=(offline_helper.coin_name(highest_buy_order.symbol), 'wallex')
            ).start()
            return False

        # Check for threaded

        if threaded is True:
            executor = self._get_executor(3, 'BuyBuySell')
        else:
            executor = None

        # place orders

        try:
            one_symbol = lowest_sell_order.symbol
            one_qty = round(lowest_sell_quantity_for_arbitrage, WallexInfoCacher.get_qty_round_point(one_symbol))
            one_price = round(lowest_sell_order.price, WallexInfoCacher.get_price_round_point(one_symbol))

            if threaded is True and executor is not None:
                one = executor.submit(
                    self.__wl.create_order,
                    symbol=one_symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price),
                )
            else:
                one = self.__wl.create_order(
                    symbol=one_symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price),
                )
        except Exception as e:
            print(f'{e=}')
            one = None

        try:
            three_symbol = highest_buy_order.symbol
            three_qty = round(highest_buy_quantity_for_arbitrage, WallexInfoCacher.get_qty_round_point(three_symbol))
            three_price = round(highest_buy_order.price, WallexInfoCacher.get_price_round_point(three_symbol))

            if threaded is True and executor is not None:
                three = executor.submit(
                    self.__binance.create_order,
                    symbol=three_symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(three_qty),
                    price=str(three_price)
                )
            else:
                three = self.__wl.create_order(
                    symbol=three_symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(three_qty),
                    price=str(three_price)
                )
        except Exception as e:
            print(f'{e=}')
            three = None

        try:
            two_qty = round(highest_buy_quantity_for_arbitrage,BinanceInfoCacher.get_step_size(binance_symbol))

            if threaded is True and executor is not None:
                two = executor.submit(
                    self.__binance.order_market_buy,
                    symbol=binance_symbol,
                    quantity=str(two_qty)
                )
            else:
                two = self.__binance.order_market_buy(
                    symbol=binance_symbol,
                    quantity=str(two_qty)
                )
        except Exception as e:
            print(f'{e=}')
            two = None

        if threaded is True and executor is not None:
            if one is not None:
                one = one.result()
            if two is not None:
                two = two.result()
            if three is not None:
                three = three.result()

        AfterArbitrageHandler(self.__wl, self.__binance, [one, two, three], revert_on_exception)

    def _buy_sell_sell_arbitrage(
            self,
            highest_buy_order: WallexOrder,
            lowest_sell_order: WallexOrder,
            threaded: bool = False,
            revert_on_exception: bool = False
    ) -> bool:
        """
        Buy highest buy order and sell lowest sell order

        :param highest_buy_order: Highest buy order data
        :type highest_buy_order: WallexOrder

        :param lowest_sell_order: Lowest sell order data
        :type lowest_sell_order: WallexOrder

        :return: True if arbitrage is possible
        :rtype: bool
        """

        binance_symbol, binance_src, binance_dst, binance_src_price, binance_dst_price, binance_rate = \
            offline_helper.find_binance_symbol_binance_src_binance_dst_src_price_dst_price_rate(
                lowest_sell_order,
                highest_buy_order,
            )

        wallex_tmn_balance, wallex_coin_balance, binance_coin_balance = self._find_balances(
            wallex_coin=offline_helper.coin_name(highest_buy_order.symbol),
            binance_coin_one=binance_src.upper(),
        )

        base_lowest_quantity_in_usdt = min(highest_buy_order.volume_in_usdt, lowest_sell_order.volume_in_usdt)
        highest_buy_quantity_for_arbitrage = base_lowest_quantity_in_usdt / highest_buy_order.binance_price
        lowest_sell_quantity_for_arbitrage = base_lowest_quantity_in_usdt / lowest_sell_order.binance_price

        # print all data
        print(f'{highest_buy_order=} \n{lowest_sell_order=} \n{binance_symbol=} \n{binance_src=} \n{binance_dst=} \n'
              f'{binance_src_price=} \n{binance_dst_price=} \n{binance_rate=} \n'
              f'{wallex_tmn_balance=} \n{binance_coin_balance=} \n{wallex_coin_balance=} \n'
              f'{highest_buy_quantity_for_arbitrage=} \n{lowest_sell_quantity_for_arbitrage=} \n')
        print(f'----------------------------------')

        if wallex_tmn_balance < lowest_sell_quantity_for_arbitrage * lowest_sell_order.price:
            Thread(
                target=self._handle_insufficient_funds,
                args=('TMN', 'wallex')
            ).start()
            return False

        if binance_coin_balance < highest_buy_quantity_for_arbitrage * binance_rate:
            Thread(
                target=self._handle_insufficient_funds,
                args=(binance_src.upper(), 'wallex')
            ).start()
            return False

        if wallex_coin_balance < highest_buy_quantity_for_arbitrage:
            Thread(
                target=self._handle_insufficient_funds,
                args=(offline_helper.coin_name(highest_buy_order.symbol), 'wallex')
            ).start()
            return False

        # Check for threaded

        if threaded is True:
            executor = self._get_executor(3, 'BuySellSell')
        else:
            executor = None

        # place orders

        try:
            one_symbol = lowest_sell_order.symbol
            one_qty = round(lowest_sell_quantity_for_arbitrage,WallexInfoCacher.get_qty_round_point(one_symbol))
            one_price = round(lowest_sell_order.price,WallexInfoCacher.get_price_round_point(one_symbol))

            if threaded is True and executor is not None:
                one = executor.submit(
                    self.__wl.create_order,
                    symbol=one_symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price)
                )
            else:
                one = self.__wl.create_order(
                    symbol=one_symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price)
                )
        except Exception as e:
            print(f'{e=}')
            one = None

        try:
            three_symbol = highest_buy_order.symbol
            three_qty = round(highest_buy_quantity_for_arbitrage, WallexInfoCacher.get_qty_round_point(three_symbol))
            three_price = round(highest_buy_order.price, WallexInfoCacher.get_price_round_point(three_symbol))

            if threaded is True and executor is not None:
                three = executor.submit(
                    self.__binance.create_order,
                    symbol=three_symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(three_qty),
                    price=str(three_price)
                )
            else:
                three = self.__wl.create_order(
                    symbol=three_symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(three_qty),
                    price=str(three_price)
                )
        except Exception as e:
            print(f'{e=}')
            three = None

        try:
            two_qty = round(highest_buy_quantity_for_arbitrage, BinanceInfoCacher.get_step_size(binance_symbol))
            if threaded is True and executor is not None:
                two = executor.submit(
                    self.__binance.order_market_sell,
                    symbol=binance_symbol,
                    quantity=str(two_qty)
                )
            else:
                two = self.__binance.order_market_sell(
                    symbol=binance_symbol,
                    quantity=str(two_qty)
                )
        except Exception as e:
            print(f'{e=}')
            two = None

        if threaded is True and executor is not None:
            if one is not None:
                one = one.result()
            if two is not None:
                two = two.result()
            if three is not None:
                three = three.result()

        AfterArbitrageHandler(self.__wl, self.__binance, [one, two, three], revert_on_exception)

    def _two_chain_arbitrage(
            self,
            highest_buy_order: WallexOrder,
            lowest_sell_order: WallexOrder,
            threaded: bool = False,
            revert_on_exception: bool = False
    ):

        base_lowest_quantity_in_usdt = min(highest_buy_order.volume_in_usdt, lowest_sell_order.volume_in_usdt)
        highest_buy_quantity_for_arbitrage = base_lowest_quantity_in_usdt / highest_buy_order.binance_price
        lowest_sell_quantity_for_arbitrage = base_lowest_quantity_in_usdt / lowest_sell_order.binance_price

        wallex_tmn_balance, wallex_coin_balance, binance_coin_balance_one, binance_usdt_balance = \
            self._find_balances(
                wallex_coin=offline_helper.coin_name(highest_buy_order.symbol),
                binance_coin_one=offline_helper.coin_name(lowest_sell_order.symbol),
                binance_usdt=True
            )

        if wallex_tmn_balance < lowest_sell_quantity_for_arbitrage * lowest_sell_order.price:
            Thread(
                target=self._handle_insufficient_funds,
                args=('TMN', 'wallex')
            ).start()
            return False

        if binance_coin_balance_one < lowest_sell_quantity_for_arbitrage:
            Thread(
                target=self._handle_insufficient_funds,
                args=(offline_helper.coin_name(lowest_sell_order.symbol), 'wallex')
            ).start()
            return False

        if wallex_coin_balance < highest_buy_quantity_for_arbitrage:
            Thread(
                target=self._handle_insufficient_funds,
                args=(offline_helper.coin_name(highest_buy_order.symbol), 'wallex')
            ).start()
            return False

        if binance_usdt_balance < highest_buy_quantity_for_arbitrage:
            Thread(
                target=self._handle_insufficient_funds,
                args=('USDT', 'wallex')
            ).start()
            return False

        # Check for threaded

        if threaded is True:
            executor = self._get_executor(3, 'TwoChain')
        else:
            executor = None

        # place orders

        try:
            one_symbol = lowest_sell_order.symbol
            one_qty = round(lowest_sell_quantity_for_arbitrage, WallexInfoCacher.get_qty_round_point(one_symbol))
            one_price = round(lowest_sell_order.price, WallexInfoCacher.get_price_round_point(one_symbol))

            if threaded is True and executor is not None:
                one = executor.submit(
                    self.__wl.create_order,
                    symbol=lowest_sell_order.symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price)
                )
            else:
                one = self.__wl.create_order(
                    symbol=lowest_sell_order.symbol,
                    side='buy',
                    type_='limit',
                    quantity=str(one_qty),
                    price=str(one_price)
                )
        except Exception as e:
            print(f'{e=}')
            one = None

        try:
            four_symbol = highest_buy_order.symbol
            four_qty = round(highest_buy_quantity_for_arbitrage, WallexInfoCacher.get_qty_round_point(four_symbol))
            four_price = round(highest_buy_order.price, WallexInfoCacher.get_price_round_point(highest_buy_order.symbol))

            if threaded is True and executor is not None:
                four = executor.submit(
                    self.__binance.create_order,
                    symbol=highest_buy_order.symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(four_qty),
                    price=str(four_price)
                )
            else:
                four = self.__wl.create_order(
                    symbol=highest_buy_order.symbol,
                    side='sell',
                    type_='limit',
                    quantity=str(four_qty),
                    price=str(four_price)
                )
        except Exception as e:
            print(f'{e=}')
            four = None

        try:
            two_symbol = f'{offline_helper.coin_name(lowest_sell_order.symbol)}USDT'
            two_qty = round(lowest_sell_quantity_for_arbitrage, BinanceInfoCacher.get_step_size(two_symbol))

            if threaded is True and executor is not None:
                two = executor.submit(
                    self.__binance.order_market_sell,
                    symbol=two_symbol,
                    quantity=str(two_qty)
                )
            else:
                two = self.__binance.order_market_sell(
                    symbol=two_symbol,
                    quantity=str(two_qty)
                )
        except Exception as e:
            print(f'{e=}')
            two = None

        try:
            three_symbol = f'{offline_helper.coin_name(highest_buy_order.symbol)}USDT'
            three_qty = round(highest_buy_quantity_for_arbitrage, BinanceInfoCacher.get_step_size(three_symbol))

            if threaded is True and executor is not None:
                three = executor.submit(
                    self.__binance.order_market_buy,
                    symbol=three_symbol,
                    quantity=str(three_qty)
                )
            else:
                three = self.__binance.order_market_buy(
                    symbol=three_symbol,
                    quantity=str(three_qty)
                )
        except Exception as e:
            print(f'{e=}')
            three = None

        if threaded is True and executor is not None:
            if one is not None:
                one = one.result()
            if two is not None:
                two = two.result()
            if three is not None:
                three = three.result()
            if four is not None:
                four = four.result()

        AfterArbitrageHandler(self.__wl, self.__binance, [one, two, three, four], revert_on_exception)

    def _same_coin_arbitrage(self):
        if self.__logger:
            print('Same Coin Arbitrage')
        return False

    def _find_balances(
            self, wallex_coin: str, binance_coin_one: str, binance_usdt: bool = False
    ) -> t.Union[t.Tuple[float, float, float, float], t.Tuple[float, float, float]]:
        """
        Finds the balances of the given coin in the given exchange.

        :param wallex_coin: The coin to find the balance of.
        :type wallex_coin: str

        :param binance_coin_one: The coin to find the balance of.
        :type binance_coin_one: str

        :param binance_usdt: Whether or not to find the balance of the USDT coin.
        :type binance_usdt: bool

        :return: The balances of the given coin in the given exchange.
        :rtype: t.Union[t.Tuple[float, float, float, float], t.Tuple[float, float, float]]
        """

        all_wallex_balances = self.__wallex_balances_redis.read_all_balances()

        tmn_balance = offline_helper.find_wallex_asset_balance_offline(
            all_wallex_balances,
            'TMN'
        )

        binance_coin_balance = float(self.__binance_balances_redis.read_balance(binance_coin_one.upper()))

        wallex_balance = offline_helper.find_wallex_asset_balance_offline(
            all_wallex_balances,
            wallex_coin
        )

        if binance_usdt is True:
            binance_usdt_balance = float(self.__binance_balances_redis.read_balance('USDT'))
            return tmn_balance, wallex_balance, binance_coin_balance, binance_usdt_balance

        return tmn_balance, wallex_balance, binance_coin_balance

    def run(self) -> None:
        while True:
            try:
                self.main()
                time.sleep(self.__sleep_time)
            except Exception as e:
                print(f'[ERROR] -> main() -> Exception -> \n{e}\n{pe()}')

            time.sleep(self.__sleep_time)
