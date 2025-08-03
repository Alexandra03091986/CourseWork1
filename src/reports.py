import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
from pandas import DataFrame

from config import PATH_DATA
from logger import logger


def report_to_file(filename: Optional[str] = None) -> Callable:
    """
       Декоратор для сохранения результатов отчета в файл.
       Если имя файла не указано, генерирует имя автоматически.
       """
    def inner(report_func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(report_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = report_func(*args, **kwargs)

            # Генерируем имя файла, если не указано
            if filename is None:
                file_name = "report_file.json"
            else:
                file_name = filename

            # Сохраняем результат в файл
            file_path = str(os.path.join(PATH_DATA, file_name))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if isinstance(result, pd.DataFrame):
                result.to_json(file_path, orient='records', indent=4, force_ascii=False)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)

            logger.info(f"Отчет сохранен в файл: {file_path}")

            return result
        return wrapper
    return inner


@report_to_file()       # "fast_food_report.json"
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
       Возвращает траты по заданной категории за последние три месяца.
           transactions: DataFrame с транзакциями
           category: Название категории для фильтрации
           date: Опциональная дата (формат YYYY-MM-DD). Если не указана - используется текущая дата.
       Returns:
           Отфильтрованный DataFrame с транзакциями
    """
    if date is None:
        date_dt = datetime.now()
    else:
        date_dt = datetime.strptime(date, "%Y-%m-%d")      # конец периода

    start_dt = date_dt - pd.DateOffset(months=3)                      # начало периода

    # Преобразуем даты в DataFrame к datetime
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"],
        format="%d.%m.%Y %H:%M:%S",
        dayfirst=True)

    # Фильтрация данных
    start_filter = (transactions["Дата операции"] >= start_dt)
    end_filter = (transactions["Дата операции"] <= date_dt)

    filter_amount = transactions["Сумма операции"] < 0
    filter_category = transactions["Категория"] == category

    selected_transactions: DataFrame = transactions[start_filter & end_filter & filter_amount & filter_category]
    logger.debug(f"Найдено {len(selected_transactions)} операций")

    return selected_transactions


# if __name__ == '__main__':
#     all_transactions = get_cards(PATH_XLSX)
#     report_data = spending_by_category(all_transactions, "Дом и ремонт", "2021-11-25")
#     print(report_data)
    # print(spending_by_category(all_transactions, "Дом и ремонт", "2021-11-25"))
