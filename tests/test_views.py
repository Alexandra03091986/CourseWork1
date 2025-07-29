import json
from unittest.mock import patch
from src.views import get_main_page_info
import pandas as pd
import pytest


@pytest.fixture
def mock_transactions():
    return pd.DataFrame([
        {"Дата операции": "15.01.2023 14:00:00", "Карта": "1234", "Сумма операции": 500, "Валюта": "RUB",
         "Категория": "Транспорт"},
        {"Дата операции": "20.01.2023 10:00:00", "Карта": "5678", "Сумма операции": 1000, "Валюта": "USD",
         "Категория": "Отели"},
        {"Дата операции": "31.01.2023 23:58:00", "Карта": "1234", "Сумма операции": 300, "Валюта": "RUB",
         "Категория": "Еда"},
        {"Дата операции": "20.01.2023 10:00:00", "Карта": "5678", "Сумма операции": 1000, "Валюта": "USD",
         "Категория": "Отели"},
        {"Дата операции": "31.01.2023 23:58:00", "Карта": "1234", "Сумма операции": 300, "Валюта": "RUB",
         "Категория": "Еда"}
    ])
@pytest.fixture
def mock_settings():
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"]
    }


def test_main_page_info_structure(mock_transactions, mock_settings):
    """Проверяет структуру возвращаемых данных"""
    with patch('src.utils.get_cards', return_value=mock_transactions), \
        patch('src.utils.get_greetings', return_value="Добрый день"), \
        patch('src.utils.get_user_settings', return_value=mock_settings), \
        patch('src.utils.get_currency_rates', return_value={"USD": 82.1, "EUR": 94.66}), \
        patch('src.utils.get_stock_prices', return_value={"AAPL": 150.0, "GOOGL": 2500.0}), \
        patch('src.utils.get_top_five_max_prices') as mock_top_five, \
        patch('src.utils.get_cards_info') as mock_cards_info:

        # Настраиваем моки для дополнительных функций
        mock_top_five.return_value = [{"Дата операции": "15.01.2023", "Сумма": 500, "Категория": "Транспорт"}, \
        {"Дата операции": "01.01.2023", "Сумма": 100, "Категория": "Еда"}]
        mock_cards_info.return_value = [{"card": "1234", "balance": 1000}]

        # Вызываем тестируемую функцию
        result_json = get_main_page_info("2023-01-31 23:59:59")
        result = json.loads(result_json)

        # Проверяем структуру ответа
        assert "greeting" in result
        assert "cards" in result
        assert "top_transactions" in result
        assert "currency_rates" in result
        assert "stock_prices" in result

        # Проверяем, что моки сработали
        assert result["greeting"] == "Добрый день"
        assert result["currency_rates"] == {"USD": 75.0, "EUR": 85.0}
        assert result["stock_prices"] == {"AAPL": 150.0, "GOOGL": 2500.0}
        assert len(result["top_transactions"]) == 2
        assert len(result["cards"]) == 1



