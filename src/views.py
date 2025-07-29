import json
import pandas as pd

from typing import Any
from datetime import datetime
from config import PATH_XLSX, USER_SETTINGS
from src.utils import get_greetings, get_cards, get_top_five_max_prices, get_cards_info, get_user_settings, \
    get_currency_rates, get_stock_prices
from logger import logger

def get_main_page_info(date: Any):
    """ Главную функцию, принимающую на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
     и возвращающую JSON-ответ со следующими данными:
     1. Приветствие
     2. По каждой карте
     3. Топ-5 транзакций по сумме платежа
     4. Курс валют
     5. Стоимость акций из S&P500
     """
    # 1. Получение приветствия
    logger.info(f"Запуск формирования отчета для даты: {date}")
    logger.info("Получаем персональное приветствие")
    greetings = get_greetings()
    logger.debug(f"Приветствие: {greetings}")

    # 2. Обработка карт и транзакций
    logger.info("Загрузка данных по картам и транзакциям")
    all_transactions = get_cards(PATH_XLSX)
    logger.info(f"Всего транзакций загружено: {len(all_transactions)}")
    # Преобразуем строку в объект datetime   YYYY-MM-DD HH:MM:SS
    end_period = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    logger.info(f"Преобразуем строку в объект datetime YYYY-MM-DD HH:MM:SS {end_period}")
    start_period = end_period.replace(day=1, hour=0, minute=0, second=0)
    logger.info(f"Анализируем период с {start_period} по {end_period}")

    # Фильтрация транзакций
    selected_transactions = all_transactions[(pd.to_datetime(all_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True) >= start_period) & (pd.to_datetime(all_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True) <= end_period)]
    logger.info(f"Отфильтровано транзакций за период: {len(selected_transactions)}")

    # 3. Анализ карт
    card_info = get_cards_info(selected_transactions)
    logger.info(f"Получена информация по {len(card_info)} картам")

    # 4. Топ-5 транзакций
    top_five = get_top_five_max_prices(selected_transactions)
    logger.info("Сформирован топ-5 транзакций.")

    # 5. Финансовые данные
    logger.info("Загрузка финансовых данных")
    stock_currencies = get_user_settings(USER_SETTINGS)
    logger.debug(f"Настройки пользователя: {stock_currencies}")

    currencies = stock_currencies["user_currencies"]
    stocks = stock_currencies["user_stocks"]

    logger.info(f"Запрашиваем курсы валют: {', '.join(currencies)}")
    currency_rates = get_currency_rates(currencies)

    logger.info(f"Запрашиваем котировки акций: {', '.join(stocks)}")
    stock_prices = get_stock_prices(stocks)

    # Формирование результата
    result = {
        "greeting": greetings,
        "cards": card_info,
        "top_transactions": top_five,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    logger.info("Отчет успешно сформирован")
    return json.dumps(result, indent=2, ensure_ascii=False)


# if __name__ == '__main__':
#     print(get_main_page_info("11.01.2018 17:21:40"))
