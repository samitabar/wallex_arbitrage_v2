__all__ = [
    'WALLEX_SYMBOLS',
    'CURRENCIES',
    'BTC_EXCEPTIONS',
    'ETH_EXCEPTIONS',
    'BNB_EXCEPTIONS',
    'BTC_ETH_BNB_USDT',
    'COINS_MINUS_BTC_ETH_USDT',
    'COINS_MINUS_BTC_ETH_BNB_USDT',
    'COINS_MINUS_USDT',
    'COINS_PLUS_USDT',
    'BTC_ETH_BNB'
]

WALLEX_SYMBOLS = [
    'BTCTMN',
    'ETHTMN',
    'DOGETMN',
    'BCHTMN',
    'LTCTMN',
    'DASHTMN',
    'USDTTMN',
    'XRPTMN',
    'XLMTMN',
    'EOSTMN',
    'TRXTMN',
    'ADATMN',
    'BNBTMN',
    'ATOMTMN',
    'MATICTMN',
    'FTMTMN',
    'DOTTMN',
    'FILTMN',
    'CAKETMN',
    'LINKTMN',
    'UNITMN',
    'RUNETMN',
    'CHZTMN',
    'BTTCTMN',
    'MANATMN',
    'AXSTMN',
    'SANDTMN',
    'ENJTMN',
    'ALICETMN',
]

CURRENCIES = [
    'btctmn',
    'ethtmn',
    'bchtmn',
    'dashtmn',
    'ltctmn',
    'usdttmn',
    'xrptmn',
    'trxtmn',
    'xlmtmn',
    'dogetmn',
    'eostmn',
    'adatmn',
    'bnbtmn',
    'atomtmn',
    'matictmn',
    'ftmtmn',
    'dottmn',
    'filtmn',
    'shibtmn',
    'caketmn',
    'linktmn',
    'unitmn',
    'runetmn',
    'chztmn',
    'bttctmn',
    'alicetmn',
    'manatmn',
    'axstmn',
    'sandtmn',
    'enjtmn',
]


BTC_EXCEPTIONS = [
    'shibtmn',
    'bttctmn',
]

ETH_EXCEPTIONS = [
    'shibtmn',
    'filtmn',
    'atomtmn',
    'matictmn',
    'linktmn',
    'caketmn',
    'dogetmn',
    'unitmn',
    'dottmn',
    'runetmn',
    'bttctmn',
    'chztmn',
    'bchtmn',
    'alicetmn',
]

BNB_EXCEPTIONS = [
    'shibtmn',
    'dogetmn',
    'linktmn',
]

ALL_NEEDED_PRICE = []
BTC_ETH_BNB_USDT = ['btctmn', 'ethtmn', 'bnbtmn', 'usdttmn']

for _coin in CURRENCIES:
    if _coin != 'usdttmn':
        ALL_NEEDED_PRICE.append(_coin.upper().split('TMN')[0] + 'USDT')
    if _coin not in BTC_EXCEPTIONS and _coin not in BTC_ETH_BNB_USDT:
        ALL_NEEDED_PRICE.append(_coin.upper().split('TMN')[0] + 'BTC')
    if _coin not in ETH_EXCEPTIONS and _coin not in BTC_ETH_BNB_USDT:
        ALL_NEEDED_PRICE.append(_coin.upper().split('TMN')[0] + 'ETH')
    if _coin not in BNB_EXCEPTIONS and _coin not in BTC_ETH_BNB_USDT:
        ALL_NEEDED_PRICE.append(_coin.upper().split('TMN')[0] + 'BNB')
    ALL_NEEDED_PRICE.append('BNBBTC')
    ALL_NEEDED_PRICE.append('ETHBTC')
    ALL_NEEDED_PRICE.append('BNBETH')


COINS_MINUS_BTC_ETH_USDT = CURRENCIES.copy()
COINS_MINUS_BTC_ETH_USDT.remove('btctmn')
COINS_MINUS_BTC_ETH_USDT.remove('ethtmn')
COINS_MINUS_BTC_ETH_USDT.remove('usdttmn')

COINS_MINUS_BTC_ETH_BNB_USDT = CURRENCIES.copy()
COINS_MINUS_BTC_ETH_BNB_USDT.remove('btctmn')
COINS_MINUS_BTC_ETH_BNB_USDT.remove('ethtmn')
COINS_MINUS_BTC_ETH_BNB_USDT.remove('bnbtmn')
COINS_MINUS_BTC_ETH_BNB_USDT.remove('usdttmn')

COINS_MINUS_USDT = CURRENCIES.copy()
COINS_MINUS_USDT.remove('usdttmn')

COINS_PLUS_USDT = COINS_MINUS_BTC_ETH_USDT.copy()
COINS_PLUS_USDT.append('usdttmn')

BTC_ETH_BNB = ['btctmn', 'ethtmn', 'bnbtmn']

SIDES = ['ask', 'bid']

