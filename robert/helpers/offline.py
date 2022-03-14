import typing as t

from ..exceptions import DeciderException
from ..constants.symbol_constants import *
from ..helpers.models import BinancePaths, WallexOrder

PRICE_ROUND_POINTS = {}
QTY_ROUND_POINTS = {}


def coin_name(coin: t.Text) -> t.Text:
    coin = coin.upper()
    coin_split = coin.split('TMN') if coin.endswith('TMN') else \
        coin.split('USDT') if coin.endswith('USDT') and not coin.startswith('USDT') else coin.split(
            'BTC') if coin.endswith('BTC') and not coin.startswith('BTC') else coin
    _coin = coin_split[0] if len(coin_split) > 1 and type(coin_split) == list else coin

    return _coin


def get_key_from_dict(my_dict: t.Dict, val: t.Any) -> t.Text:
    for key, value in my_dict.items():
        if val == value:
            return key


def find_wallex_asset_balance_offline(balances: t.Dict, asset: t.Text) -> float:
    coin = balances.get(asset.upper())
    return float(coin.get('value')) - float(coin.get('locked'))


def calculate_remaining_amount(order: t.Dict) -> float:
    sym = order.get('symbol').upper()
    orig_qty = round(float(order.get('origQty')), QTY_ROUND_POINTS.get(sym))
    executed_qty = round(float(order.get('executedQty')), QTY_ROUND_POINTS.get(sym))
    amount = orig_qty - executed_qty

    return amount


def calculate_loss(rechecked_order: t.Dict, marketed_order: t.Dict) -> float:
    symbol = rechecked_order.get('symbol').upper()
    amount = round((float(marketed_order.get('executedQty'))), QTY_ROUND_POINTS.get(symbol))

    current_price = round(
        float(marketed_order.get('fills')[0].get('price')),
        PRICE_ROUND_POINTS.get(symbol)
    )

    if rechecked_order.get('side').lower() == 'buy':
        diff_price = round((float(current_price) - float(rechecked_order.get('price'))), QTY_ROUND_POINTS.get(symbol))
        loss = int(float(amount) * float(diff_price))
    else:
        diff_price = round((float(rechecked_order.get('price')) - float(current_price)), QTY_ROUND_POINTS.get(symbol))
        loss = int(float(amount) * float(diff_price))

    return loss


def filter_orderbook(orderbook: t.Dict[str, t.List[t.Dict]], min_volume: float = 300000) -> t.Dict:
    _orderbook = {
        'bid': [],
        'ask': [],
    }

    buyers = orderbook.get('bid')
    sellers = orderbook.get('ask')

    buyer_i = 0
    for order in buyers:
        if float(order.get('sum')) >= min_volume:
            break
        buyer_i += 1

    seller_i = 0
    for order in sellers:
        if float(order.get('sum')) >= min_volume:
            break
        seller_i += 1

    _orderbook['bid'] = buyers[buyer_i:]
    _orderbook['ask'] = sellers[seller_i:]

    return _orderbook


def calculate_gap_percent(high_price: float, low_price: float) -> float:
    return (high_price / low_price) - 1


def binance_symbol_decider(lowest_sell_market: str, highest_buy_market: str) -> t.Tuple[str, str, str]:

    lowest_sell_market = lowest_sell_market.lower()
    highest_buy_market = highest_buy_market.lower()

    if 'btc' in lowest_sell_market and 'eth' in highest_buy_market:
        symbol = f"{highest_buy_market.split('tmn')[0].upper()}{lowest_sell_market.split('tmn')[0].upper()}"
        src = highest_buy_market.split('tmn')[0].upper()
        dst = lowest_sell_market.split('tmn')[0].upper()

    elif ('btc' in lowest_sell_market or 'eth' in lowest_sell_market or
          'bnb' in lowest_sell_market) and \
            highest_buy_market.lower() in COINS_MINUS_BTC_ETH_USDT:
        symbol = f"{highest_buy_market.split('tmn')[0].upper()}{lowest_sell_market.split('tmn')[0].upper()}"
        src = highest_buy_market.split('tmn')[0].upper()
        dst = lowest_sell_market.split('tmn')[0].upper()

    elif 'eth' in lowest_sell_market and 'btc' in highest_buy_market:
        symbol = f"{lowest_sell_market.split('tmn')[0].upper()}{highest_buy_market.split('tmn')[0].upper()}"
        src = lowest_sell_market.split('tmn')[0].upper()
        dst = highest_buy_market.split('tmn')[0].upper()

    elif 'usdt' in highest_buy_market:
        symbol = f"{lowest_sell_market.split('tmn')[0].upper()}{highest_buy_market.split('tmn')[0].upper()}"
        src = lowest_sell_market.split('tmn')[0].upper()
        dst = highest_buy_market.split('tmn')[0].upper()

    elif 'usdt' in lowest_sell_market and (highest_buy_market.lower() in COINS_MINUS_USDT):
        symbol = f"{highest_buy_market.split('tmn')[0].upper()}{lowest_sell_market.split('tmn')[0].upper()}"
        src = highest_buy_market.split('tmn')[0].upper()
        dst = lowest_sell_market.split('tmn')[0].upper()

    elif ('btc' in highest_buy_market or 'eth' in highest_buy_market or
          'bnb' in highest_buy_market) \
            and lowest_sell_market.lower() in COINS_MINUS_BTC_ETH_USDT:
        symbol = f"{lowest_sell_market.split('tmn')[0].upper()}{highest_buy_market.split('tmn')[0].upper()}"
        src = lowest_sell_market.split('tmn')[0].upper()
        dst = highest_buy_market.split('tmn')[0].upper()

    else:
        raise DeciderException(
            'binance_symbol_decider',
            f'Jesus Christ WTF | {lowest_sell_market} - {highest_buy_market}'
        )

    return symbol, src, dst


def path_decider(lowest_sell_market: str, highest_buy_market: str) -> t.Union[str, BinancePaths]:
    lowest_sell_market = lowest_sell_market.lower()
    highest_buy_market = highest_buy_market.lower()

    if ('bnb' in lowest_sell_market and highest_buy_market in BNB_EXCEPTIONS) or (
            lowest_sell_market in BNB_EXCEPTIONS and 'bnb' in highest_buy_market):
        return BinancePaths.TwoChain

    elif ('eth' in lowest_sell_market and highest_buy_market in ETH_EXCEPTIONS) or (
            lowest_sell_market in ETH_EXCEPTIONS and 'eth' in highest_buy_market):
        return BinancePaths.TwoChain

    elif ('btc' in lowest_sell_market and highest_buy_market in BTC_EXCEPTIONS) or (
            lowest_sell_market in BTC_EXCEPTIONS and 'btc' in highest_buy_market):
        return BinancePaths.TwoChain

    elif lowest_sell_market == highest_buy_market:
        return BinancePaths.SameCoin

    elif 'btc' in lowest_sell_market and ('eth' in highest_buy_market or 'bnb' in highest_buy_market):
        return BinancePaths.BuyBuySell
    elif 'btc' in lowest_sell_market and highest_buy_market in COINS_MINUS_BTC_ETH_USDT:
        return BinancePaths.BuyBuySell
    elif 'eth' in lowest_sell_market and highest_buy_market in COINS_MINUS_BTC_ETH_USDT:
        return BinancePaths.BuyBuySell
    elif 'bnb' in lowest_sell_market and highest_buy_market in COINS_MINUS_BTC_ETH_USDT:
        return BinancePaths.BuyBuySell
    elif 'usdt' in lowest_sell_market and highest_buy_market in COINS_MINUS_USDT:
        return BinancePaths.BuyBuySell

    elif 'btc' in lowest_sell_market and 'usdt' in highest_buy_market:
        return BinancePaths.BuySellSell
    elif 'eth' in lowest_sell_market and 'usdt' in highest_buy_market:
        return BinancePaths.BuySellSell
    elif 'bnb' in lowest_sell_market and 'usdt' in highest_buy_market:
        return BinancePaths.BuySellSell
    elif lowest_sell_market in COINS_MINUS_BTC_ETH_BNB_USDT and 'usdt' in highest_buy_market:
        return BinancePaths.BuySellSell
    elif lowest_sell_market in COINS_MINUS_USDT and highest_buy_market in BTC_ETH_BNB:
        return BinancePaths.BuySellSell

    elif lowest_sell_market in COINS_MINUS_BTC_ETH_BNB_USDT and highest_buy_market in COINS_MINUS_BTC_ETH_BNB_USDT:
        return BinancePaths.TwoChain

    else:
        raise DeciderException('path_decider', f'Invalid Pairs -> {lowest_sell_market} - {highest_buy_market}')


def find_binance_price_from_wallex_order(coin: str, wallex_orders: t.Tuple[WallexOrder, WallexOrder]) -> float:
    for order in wallex_orders:
        if coin_name(order.symbol) == coin:
            return order.binance_price

    raise DeciderException('find_binance_price_from_wallex_order', f'Could not find {coin} in {wallex_orders}')


def find_binance_symbol_binance_src_binance_dst_src_price_dst_price_rate(
        lowest_sell_order: WallexOrder, highest_buy_order: WallexOrder
) -> t.Tuple[str, str, str, float, float, float]:

    binance_symbol, binance_src, binance_dst = binance_symbol_decider(
        lowest_sell_market=lowest_sell_order.symbol,
        highest_buy_market=highest_buy_order.symbol
    )

    binance_src_price = find_binance_price_from_wallex_order(
        binance_src, (highest_buy_order, lowest_sell_order)
    )
    binance_dst_price = find_binance_price_from_wallex_order(
        binance_dst, (highest_buy_order, lowest_sell_order)
    )

    binance_rate = binance_src_price / binance_dst_price

    return binance_symbol, binance_src, binance_dst, binance_src_price, binance_dst_price, binance_rate
