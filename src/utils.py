import json
import os
import pandas as pd

import requests
from datetime import datetime
from dotenv import load_dotenv
from config import USER_SETTINGS, PATH_XLSX

# Загружаем переменные из .env
load_dotenv()


def get_greetings() -> str:
    """ Приветствие в формате "???", где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в
    зависимости от текущего времени."""
    now = int(datetime.now().strftime('%H'))
    if 6 <= now < 10:
        return "Доброе утро"
    elif 10 <= now < 18:
        return "Добрый день"
    elif 18 <= now < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_cards(path=PATH_XLSX):
    """ По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей)."""
    df = pd.read_excel(path)
    filter_df = df[df["Сумма операции"] < 0]
    sum_group = filter_df.groupby("Номер карты")["Сумма операции"].sum()
    list_sum_group = sum_group.to_dict()
    result = []
    for k, v in list_sum_group.items():
        result.append({"last_digits": k[1:], "total_spent": v * (-1), "cashback": round(v / 100 * (-1), 2)})
    return result


def get_top_five_max_prices(path=PATH_XLSX):
    """ Топ-5 транзакций по сумме платежа. """
    df = pd.read_excel(path)
    top_five = df.sort_values("Сумма платежа").head()
    top_transactions = top_five.to_dict("records")

    top_result = []
    for k in top_transactions:
        top_result.append({
            "date": k.get("Дата операции"),
            "amount": k.get("Сумма платежа"),
            "category": k.get("Категория"),
            "description": k.get("Описание")
        })
    return top_result       # красиво выведет в консоль если прописать так:
                            # json.dumps(top_result, indent=4, ensure_ascii=False)


def get_user_settings() -> dict:
    """ Функция чтения пользовательских настроек."""
    with open(USER_SETTINGS, "r", encoding="utf-8") as file:
        settings = json.load(file)
        return settings


def get_api_currency(currency):
    """Функция возвращает текущий курс валюты по API"""
    rate = "RUB"
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={rate}&base={currency}"

    headers = {"apikey": os.getenv("API_KEY_FOR_CURRENCY")}
    response = requests.get(url, headers=headers, data={})
    data = response.json()
    rates = data["rates"]["RUB"]
    return rates


def get_api_stocks(stocks):
    """Функция возвращает текущий курс акции по API"""
    api_key = os.getenv("API_KEY_FOR_STOCKS")
    url = f"https://api.twelvedata.com/price?symbol={stocks}&apikey={api_key}&source=docs"
    response = requests.get(url)
    data = response.json()
    return data


def user_currency_rates():
    """ Функция возвращает курс валют."""
    user_settings = get_user_settings()
    user_currencies = user_settings["user_currencies"]
    currency_rates = []        # валюта в реальном времени
    for currency in user_currencies:
        rates = get_api_currency(currency)
        currency_rates.append({"currency": currency, "rate": round(rates, 2)})
    return currency_rates


def user_stock_prices():
    """ Функция возвращает курс на акции пользователя"""
    user_settings = get_user_settings()
    user_stocks = user_settings["user_stocks"]
    stock_prices = []
    for stock in user_stocks:
        prices = get_api_stocks(stock)
        rounded_price = round(float(prices["price"]), 2)    # Преобразуем в float и округляем
        stock_prices.append({"stock": stock, "price": rounded_price})
    return stock_prices


if __name__ == '__main__':
    # print(get_greetings())
    # print(get_cards())
    # print(get_top_five_max_prices())
    # print(get_user_settings())
    # print(get_api_currency("EUR"))
    # print(currency_rates())
    # print(get_api_stocks("TSLA"))
    print(user_stock_prices())