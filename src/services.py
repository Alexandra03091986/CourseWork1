import json
import re
from typing import List, Dict, Any

from logger import logger


def get_search_for_transfers_to_individuals(transactions: List[Dict[str, Any]], keyword: str) -> str:
    """
    Функция возвращает JSON со всеми транзакциями, которые:
    1. Относятся к указанной категории (keyword)
    2. В описании содержат имя и инициал фамилии (например, "Иван С.")
    Аргументы:
        transactions: Путь к файлу с транзакциями
        keyword: Ключевое слово для фильтрации категории
    """

    logger.info(f"Начало фильтрации транзакций. Категория: '{keyword}'")
    logger.debug(f"Получено {len(transactions)} транзакций для обработки")

    # Компиляция регулярного выражения для поиска "Имя Ф."
    logger.debug("Компиляция регулярного выражения для поиска: Имя Ф.")
    pattern = re.compile(r"\b[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.", flags=re.IGNORECASE)
    logger.info("Регулярное выражение успешно скомпилировано")

    # Фильтрация транзакций
    filter_by_category = []
    logger.debug("Начало обработки транзакций...")
    for category in transactions:
       if keyword.lower() in str(category.get("Категория", "")).lower() and pattern.search(str(category.get("Описание", ""))):
            filter_by_category.append(category)

    logger.info(f"Найдено {len(filter_by_category)} подходящих транзакций")
    logger.debug(f"Список отфильтрованных транзакций {json.dumps(filter_by_category, indent=2, ensure_ascii=False)}")
    logger.info(f"Фильтрация завершена успешно.")
    return json.dumps(filter_by_category, indent=2, ensure_ascii=False)

# if __name__ == '__main__':
#     print(get_search_for_transfers_to_individuals(PATH_XLSX, "Переводы"))
