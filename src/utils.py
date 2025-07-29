import json
import os
import pandas as pd

import requests
from datetime import datetime
from dotenv import load_dotenv
from config import PATH_XLSX
from logger import logger


# Загружаем переменные из .env
load_dotenv()


def get_greetings() -> str:
    """ Возвращает приветствие с учётом времени.
     — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в
    зависимости от текущего времени."""
    now = int(datetime.now().strftime('%H'))
    logger.info("Преобразование строки, отформатированной в час, в целое число.")
    if 6 <= now < 10:
        logger.debug("Выбрано приветствие: Доброе утро (6-10 часов)")
        return "Доброе утро"
    elif 10 <= now < 18:
        logger.debug("Выбрано приветствие: Добрый день (10-18 часов)")
        return "Добрый день"
    elif 18 <= now < 22:
        logger.debug("Выбрано приветствие: Добрый вечер (18-22 часов)")
        return "Добрый вечер"
    else:
        logger.debug("Выбрано приветствие: Доброй ночи (23 - 6 часов)")
        return "Доброй ночи"


def get_cards(path=PATH_XLSX) -> pd.DataFrame:
    """ Функция загружает данные из Excel-файла и возвращает DataFrame"""
    logger.info(f"Загрузка данных из файла: {path}")
    df = pd.read_excel(path)
    logger.info(f"Файл {path} успешно загружен")
    # list_df = df.to_dict("records")
    return df


def get_cards_info(transactions_df: pd.DataFrame) -> list:
    """ По каждой карте:
     {
     "last_digits": "последние 4 цифры карты",
      "total_spent": общая сумма расходов,
      "cashback": кешбэк (1 рубль на каждые 100 рублей)
      }"""
    logger.info("Начало обработки информации по картам")
    filter_df = transactions_df[transactions_df["Сумма операции"] < 0]
    logger.debug(f"Найдено {len(filter_df)} операций")
    sum_group = filter_df.groupby("Номер карты")["Сумма операции"].sum()
    logger.debug(f"Обработано {len(sum_group)} карт")
    list_sum_group = sum_group.to_dict()
    result = []
    for k, v in list_sum_group.items():
        v = abs(v)
        round_v = round(v / 100, 2)
        result.append({
            "last_digits": str(k)[-4:],
            "total_spent": v,
            "cashback": round_v})
        logger.debug(f"Карта {str(k)[-4:]}: потрачено {v}, кешбэк {round_v}")
    logger.info(f"Успешно обработано {len(result)} карт")
    return result


def get_top_five_max_prices(transactions_df: pd.DataFrame) -> list:
    """ Топ-5 транзакций по сумме платежа. """
    logger.info("Начало обработки топ-5 транзакций")
    logger.debug(f"Получено {len(transactions_df)} транзакций для анализа")
    logger.debug("Сортировка транзакций по сумме платежа")
    top_five = transactions_df.sort_values("Сумма платежа", ascending=False).head()
    logger.debug("Отобрано топ-5 транзакций")
    top_transactions = top_five.to_dict("records")

    top_result = []
    for k in top_transactions:
        top_result.append({
            "date": k.get("Дата операции"),
            "amount": k.get("Сумма платежа"),
            "category": k.get("Категория"),
            "description": k.get("Описание")
        })
    logger.info(f"Успешно сформирован топ-5 транзакций (получено {len(top_result)} записей)")
    return top_result       # красиво выведет в консоль если прописать так:
                            # json.dumps(top_result, indent=4, ensure_ascii=False)


def get_user_settings(path: str) -> dict:
    """ Функция чтения пользовательских настроек из JSON-файла."""
    logger.info(f"Начало загрузки пользовательских настроек из файла: {path}")
    with open(path, "r", encoding="utf-8") as file:
        settings = json.load(file)
        logger.info("Настройки успешно загружены.")
        return settings


def get_api_currency(currency: str) -> float:
    """Функция возвращает текущий курс валюты к RUB через API"""
    rate = "RUB"
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={rate}&base={currency}"
    logger.debug(f"Формирование запроса к API: {url}")

    headers = {"apikey": os.getenv("API_KEY_FOR_CURRENCY")}
    response = requests.get(url, headers=headers, data={})
    data = response.json()
    rates = data["rates"]["RUB"]
    logger.info(f"Успешно получен курс {currency}: {rates} RUB")
    logger.debug(f"Полный ответ API: {json.dumps(data, indent=2)}")
    return rates


def get_api_stocks(stocks):
    """Функция возвращает текущий курс акции через API"""
    logger.info(f"Начало запроса для акции: {stocks}")
    api_key = os.getenv("API_KEY_FOR_STOCKS")
    url = f"https://api.twelvedata.com/price?symbol={stocks}&apikey={api_key}&source=docs"

    response = requests.get(url)
    data = response.json()

    logger.info(f"Данные по акции {stocks} успешно получены")
    logger.debug(f"Ответ API: {json.dumps(data, indent=2)}")
    return data


def get_currency_rates(user_currencies):
    """ Функция возвращает курс валют."""
    # user_settings = get_user_settings()
    # user_currencies = user_settings["user_currencies"]
    logger.info(f"Начало обработки запроса курса валют. Количество валют: {len(user_currencies)}")
    currency_rates = []        # валюта в реальном времени
    for currency in user_currencies:
        logger.info(f"Обрабатываю валюту: {currency}")
        rates = get_api_currency(currency)
        currency_rates.append({"currency": currency, "rate": round(rates, 2)})
        logger.info(f"Успешно получен курс {currency}: {round(rates, 2)}")
    logger.info(f"Обработка завершена. Успешно получено курсов: {len(user_currencies)}")
    return currency_rates


def get_stock_prices(user_stocks):
    """ Функция возвращает курс акций пользователя"""
    # user_settings = get_user_settings()
    # user_stocks = user_settings["user_stocks"]
    logger.info(f"Начало обработки запроса акций. Количество акций: {len(user_stocks)}")
    stock_prices = []
    for stock in user_stocks:
        logger.info(f"Обработка акции")
        prices = get_api_stocks(stock)
        rounded_price = round(float(prices["price"]), 2)    # Преобразуем в float и округляем
        stock_prices.append({"stock": stock, "price": rounded_price})
        logger.info(f"Успешно обработана акция {stock}: {rounded_price}")
    logger.info(f"Завершение обработки. Успешно обработано {len(stock_prices)}/{len(user_stocks)} акций")
    return stock_prices


# if __name__ == '__main__':
    # print(get_greetings())
    # print(get_cards())
    # print(get_cards_info())
    # all_transactions = get_cards(PATH_XLSX)
    # print(get_top_five_max_prices(all_transactions))
    # print(get_user_settings())
    # print(get_api_currency("EUR"))
    # print(get_currency_rates())
    # print(get_api_stocks("TSLA"))
    # print(get_stock_prices())
