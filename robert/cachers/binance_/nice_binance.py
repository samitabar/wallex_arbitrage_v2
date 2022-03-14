from binance import AsyncClient, ThreadedWebsocketManager


__all__ = [
    'AsyncNiceBinance'
]


class AsyncNiceBinance:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = AsyncClient(api_key, api_secret) if api_key and api_secret else AsyncClient()
        self.balances_ws = ThreadedWebsocketManager(api_key, api_secret)
        self.price_ws = ThreadedWebsocketManager()

    async def get_balances(self):
        balances = await self.client.get_account()
        return balances

    async def get_balance(self, symbol):
        balance = await self.client.get_asset_balance(symbol)
        return balance

    async def get_info(self, symbol: str):
        info = await self.client.get_symbol_info(symbol)
        return info
