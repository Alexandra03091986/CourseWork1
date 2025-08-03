import json
from typing import Any, Dict, Iterator, List, Union
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import get_main_page_info

# Фиктивные данные для тестов
MOCK_TRANSACTIONS = pd.DataFrame({
    "Дата операции": ["01.03.2024 10:00:00", "15.03.2024 12:00:00", "20.03.2024 14:00:00"],
    "Сумма платежа": [100, 500, 300],
    "Номер карты": ["1111", "2222", "1111"]
})

MOCK_CARDS_INFO = [{
    "last_digits": "1111",
    "total_spent": 400,
    "cashback": 4.0
}]

MOCK_TOP_FIVE = [{
    "date": "15.03.2024 12:00:00",
    "amount": 500,
    "category": "Транспорт",
    "description": "Такси"
}]

MOCK_USER_SETTINGS = {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "GOOGL"]
}

MOCK_CURRENCY_RATES = [{"currency": "USD", "rate": 75.5}]
MOCK_STOCK_PRICES = [{"stock": "AAPL", "price": 150.25}]


@pytest.fixture
def mock_dependencies() -> Iterator[MagicMock]:
    with patch('src.views.get_greetings', return_value="Добрый день"), \
         patch('src.views.get_cards', return_value=MOCK_TRANSACTIONS), \
         patch('src.views.get_cards_info', return_value=MOCK_CARDS_INFO), \
         patch('src.views.get_top_five_max_prices', return_value=MOCK_TOP_FIVE), \
         patch('src.views.get_user_settings', return_value=MOCK_USER_SETTINGS), \
         patch('src.views.get_currency_rates', return_value=MOCK_CURRENCY_RATES), \
         patch('src.views.get_stock_prices', return_value=MOCK_STOCK_PRICES), \
         patch('src.views.logger') as mock_logger:
        yield mock_logger


def test_date_parsing(mock_dependencies: MagicMock) -> None:
    """Тест корректного преобразования даты"""
    result = get_main_page_info("2024-03-15 14:30:00")
    # Проверяем что функция вернула результат
    assert result is not None
    mock_dependencies.info.assert_any_call(
        "Преобразуем строку в объект datetime YYYY-MM-DD HH:MM:SS 2024-03-15 14:30:00"
    )


def test_invalid_date_format() -> None:
    """Тест обработки некорректного формата даты"""
    with pytest.raises(ValueError):
        get_main_page_info("2024/03/15 14:30:00")


def test_transaction_filtering(mock_dependencies: MagicMock) -> None:
    """Тест фильтрации транзакций по дате"""
    get_main_page_info("2024-03-22 00:00:00")
    mock_dependencies.info.assert_any_call("Отфильтровано транзакций за период: 3")


def test_json_structure(mock_dependencies: MagicMock) -> None:
    """Тест структуры возвращаемого JSON"""
    result: Dict[str, Union[str, List[Dict[str, Any]]]] = json.loads(get_main_page_info("2024-03-15 14:30:00"))

    assert set(result.keys()) == {"greeting", "cards", "top_transactions", "currency_rates", "stock_prices"}
    assert isinstance(result["greeting"], str)
    assert isinstance(result["cards"], list)
    assert isinstance(result["top_transactions"], list)
    assert isinstance(result["currency_rates"], list)
    assert isinstance(result["stock_prices"], list)


def test_logging_sequence(mock_dependencies: MagicMock) -> None:
    """Тест последовательности логирования"""
    get_main_page_info("2024-03-15 14:30:00")

    # Проверяем последовательность ключевых логов
    log_calls: List[str] = [call[0][0] for call in mock_dependencies.info.call_args_list]
    assert "Запуск формирования отчета для даты: 2024-03-15 14:30:00" in log_calls
    assert "Загрузка данных по картам и транзакциям" in log_calls
    assert "Всего транзакций загружено:" in log_calls[3]
    assert "Сформирован топ-5 транзакций." in log_calls
    assert "Загрузка финансовых данных" in log_calls
    assert "Отчет успешно сформирован" in log_calls[-1]
