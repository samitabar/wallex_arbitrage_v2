# import logging
# from logging.handlers import TimedRotatingFileHandler
#
# from datetime import datetime
# from telegram import Bot
#
# import os
#
# from typing import Union, Tuple
#
#
# ADMIN = [417373307, 73775328]
# CHANNEL = [-1001762515038]
#
#
# bot_main = Bot('2090457609:AAFRfZWEYphuW24r2kclnN8_WTSenhdk46s')
# BOTS = [bot_main]
#
#
# # ----- # Date & time config # ----
# def current_date():
#     return str(datetime.today().strftime('%Y-%m-%d'))
#
#
# def current_time():
#     return str(datetime.now().time().strftime('%H:%M:%S'))
#
#
# if not os.path.exists('logs'):
#     os.mkdir('logs')
#
#
# # ----- # Logger config # ----
# def logger_(name: str) -> Tuple[logging.Logger, logging.Logger]:
#     _logger = logging.getLogger(f"{name}_logger")
#     _logger.setLevel(logging.DEBUG)
#
#     formatter = logging.Formatter(
#         f'[{name}-logs] - %(asctime)s - %(levelname)s - %(lineno)d: %(funcName)s[!] --> %(message)s'
#     )
#
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     _logger.addHandler(console_handler)
#
#     time_handler = TimedRotatingFileHandler(f'logs/nice/{name}-logs.log', when='midnight', backupCount=2)
#     time_handler.setFormatter(formatter)
#     _logger.addHandler(time_handler)
#
#     response_logger = logging.getLogger(f"{name}_resp_logger")
#     response_logger.setLevel(logging.DEBUG)
#
#     resp_formatter = logging.Formatter(
#         f'[{name}-resp] - %(asctime)s - %(levelname)s - %(lineno)d: %(funcName)s[!] --> %(message)s'
#     )
#
#     response_time_handler = TimedRotatingFileHandler(f'logs/resp/{name}-resp-logs.log', when='midnight', backupCount=2)
#     response_time_handler.setFormatter(resp_formatter)
#     response_logger.addHandler(response_time_handler)
#
#     return _logger, response_logger
#
#
# def disable_notification_(text: str) -> bool:
#     text = str(text).lower()
#
#     if 'notional'.lower() in text:
#         return True
#     elif 'Illegal characters'.lower() in text:
#         return True
#     elif 'invalid quantity'.lower() in text:
#         return True
#     elif 'The given data was invalid'.lower() in text:
#         return True
#     elif 'sami'.lower() in text:
#         return True
#     elif 'saman'.lower() in text:
#         return True
#     elif 'milad'.lower() in text:
#         return True
#     else:
#         return False
#
#
# def bot_logger(text: Union[Exception, str]):
#     try:
#         text = str(text)
#         text = f"[Nobitex Arbitrage]:\n\n{text}"
#
#         disable_notification = disable_notification_(text)
#
#         for x in CHANNEL:
#             for bot in BOTS:
#                 try:
#                     bot.send_message(chat_id=x, text=text, disable_notification=disable_notification)
#                     return
#                 except Exception as e:
#                     print(e)
#                     continue
#     except Exception as e:
#         print(e)
#         return
