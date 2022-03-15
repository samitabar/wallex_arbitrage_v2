import time
from threading import Thread
import typing as t

from wallex import Wallex
from binance import Client

from retry import retry


from . import offline as offline_helper


@retry()
def canceler(wl: Wallex, order: t.Union[t.Text, t.Dict]) -> t.Dict:
    if type(order) == dict:
        _ = wl.cancel_order(
            order.get('clientOrderId'),
        )
    elif type(order) == str:
        _ = wl.cancel_order(
            order,
        )
    else:
        raise TypeError(f'{type(order)} is not a valid type for canceler')

    return _


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
                canceler(
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
            _ = canceler(
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
