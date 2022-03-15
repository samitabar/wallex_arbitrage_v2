from binance import AsyncClient, ThreadedWebsocketManager, Client


__all__ = [
    'AsyncNiceBinance',
    'SyncBinance'
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

    async def get_exchange_info(self):
        info = await self.client.get_exchange_info()
        return info


class SyncBinance:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret) if api_key and api_secret else Client()

    def get_balances(self):
        balances = self.client.get_account()
        return balances

    def get_balance(self, symbol):
        balance = self.client.get_asset_balance(symbol)
        return balance

    def get_info(self, symbol: str):
        info = self.client.get_symbol_info(symbol)
        return info

    def get_exchange_info(self):
        info = self.client.get_exchange_info()
        return info
