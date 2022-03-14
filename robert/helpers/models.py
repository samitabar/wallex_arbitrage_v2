import typing as t


PRICE_ROUND_POINTS = {}
QTY_ROUND_POINTS = {}


class WallexOrder:
    def __init__(
            self, order: t.Dict[str, t.Union[str, int, float]],
            symbol: str = None, binance_price: float = 0, tether_price: int = 0,
    ):
        self.price = round((float(float(order.get("price")))), PRICE_ROUND_POINTS.get(symbol, 8))
        self.quantity = round((float(order.get("quantity"))), QTY_ROUND_POINTS.get(symbol, 8))
        self.volume = round((float(self.price * self.quantity)), PRICE_ROUND_POINTS.get(symbol, 8))
        self.symbol = symbol.upper()
        self.binance_price = float(binance_price)
        self.tether_price = int(tether_price)
        self.volume_in_usdt = self.volume / self.tether_price if self.tether_price != 0 else 0

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {'price': self.price, 'quantity': self.quantity, 'volume': self.volume}

    def from_dict(self, order_dict: t.Dict[str, t.Any]) -> 'WallexOrder':
        self.price = float(order_dict.get("price"))
        self.quantity = float(order_dict.get("quantity"))
        self.volume = self.price * self.quantity

        return self


class WallexOrderbook:
    def __init__(self, orderbook: t.Dict[str, t.Union[t.List[t.Union[t.List[str], t.Any]], str, int]]):

        self.__orderbook = orderbook

        self.__sellers = self.__orderbook["ask"]
        self.__buyers = self.__orderbook["bid"]

        self.__price = 'price'
        self.__quantity = 'quantity'
        self.__sum = 'sum'

    def __getitem__(self, item: str):
        item = item.lower()
        if 'buy' in item or 'bid' in item:
            return self.__buyers
        elif 'sell' in item or 'ask' in item:
            return self.__sellers
        else:
            raise KeyError('No such key')

    @property
    def sellers(self) -> t.List[t.List[str]]:
        return self.__sellers

    @property
    def buyers(self) -> t.List[t.List[str]]:
        return self.__buyers

    def get_order_at_index(self, buy_or_sell: str, index: int) -> t.Dict[str, t.Union[str, int, float]]:
        if buy_or_sell == "buy":
            return self.__buyers[index]
        elif buy_or_sell == "sell":
            return self.__sellers[index]
        else:
            raise ValueError("buy_or_sell must be either 'buy' or 'sell'")

    def first_order(self, buy_or_sell: str) -> WallexOrder:
        return WallexOrder(self.get_order_at_index(buy_or_sell, 0))


class WallexCreateOrder:
    def __init__(
            self, symbol: str, side: str, quantity: float, price: float, type_: str, order_id: t.Optional[str] = None
    ):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.type_ = type_
        self.order_id = order_id

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'price': self.price,
            'type': self.type_,
            'order_id': self.order_id
        }

    def from_dict(self, order_dict: t.Dict[str, t.Any]) -> 'WallexCreateOrder':
        self.symbol = order_dict.get("symbol")
        self.side = order_dict.get("side")
        self.quantity = order_dict.get("quantity")
        self.price = order_dict.get("price")
        self.type_ = order_dict.get("type")
        self.order_id = order_dict.get("order_id")

        return self


class BinancePaths:
    BuyBuySell = "buy_buy_sell"
    BuySellSell = "buy_sell_sell"
    TwoChain = 'two_chain'
    SameCoin = 'same_coin'
