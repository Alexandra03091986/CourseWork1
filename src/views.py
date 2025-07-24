import json
import pandas as pd

from typing import Any
from datetime import datetime
from config import PATH_XLSX, USER_SETTINGS
from src.utils import get_greetings, get_cards, get_top_five_max_prices, get_cards_info, get_user_settings, \
    get_currency_rates, get_stock_prices


def get_main_page_info(date: Any):
    """ Главную функцию, принимающую на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
     и возвращающую JSON-ответ со следующими данными:
     1. Приветствие
     2. По каждой карте
     3. Топ-5 транзакций по сумме платежа
     4. Курс валют
     5. Стоимость акций из S&P500
     """
    greetings = get_greetings()

    all_transactions = get_cards(PATH_XLSX)
    end_period = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    start_period = end_period.replace(day=1, hour=0, minute=0, second=0)

    selected_transactions = all_transactions[(pd.to_datetime(all_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True) >= start_period) & (pd.to_datetime(all_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True) <= end_period)]
    card_info = get_cards_info(selected_transactions)
    top_five = get_top_five_max_prices(selected_transactions)

    stock_currencies = get_user_settings(USER_SETTINGS)
    currencies = stock_currencies["user_currencies"]
    stocks = stock_currencies["user_stocks"]
    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)

    result = {
        "greeting": greetings,
        "cards": card_info,
        "top_transactions": top_five,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    return json.dumps(result, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    print(get_main_page_info("11.01.2018 17:21:40"))
