from .main import Main

from .constants import settings, symbol_constants


if __name__ == '__main__':
    m = Main(
        wallex_token=settings.WALLEX_TOKEN,
        binance_api_key=settings.BINANCE_API_KEY,
        binance_api_secret=settings.BINANCE_API_SECRET,
        symbols=symbol_constants.WALLEX_SYMBOLS,
        fee=settings.FEE,
        sleep_time=1.5,
        revert_on_exception=False,
        logger=True,
    )
    m.run()
