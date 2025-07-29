from unittest.mock import patch, Mock

import pandas as pd
import pytest

from src.utils import get_greetings, get_cards, get_cards_info, get_top_five_max_prices, get_api_currency, \
    get_api_stocks


@pytest.mark.parametrize("time_str, expected", [
    ("05", "Доброй ночи"),
    ("06", "Доброе утро"),
    ("09", "Доброе утро"),
    ("10", "Добрый день"),
    ("16", "Добрый день"),
    ("18", "Добрый вечер"),
    ("22", "Доброй ночи"),
    ("00", "Доброй ночи"),
])
def test_get_greetings(time_str, expected):
    """ Тестирует приветствие с учётом времени """
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = time_str
        assert get_greetings() == expected


@pytest.mark.parametrize("hour,expected_greeting,expected_log", [
    (7, "Доброе утро", "Выбрано приветствие: Доброе утро (6-10 часов)"),
    (12, "Добрый день", "Выбрано приветствие: Добрый день (10-18 часов)"),
    (20, "Добрый вечер", "Выбрано приветствие: Добрый вечер (18-22 часов)"),
])
def test_get_greetings_logging(caplog, hour, expected_greeting, expected_log):
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = str(hour)

        result = get_greetings()
        assert result == expected_greeting
        assert expected_log in caplog.text


def test_get_cards():
    """Тестирование функции get_cards"""
    test_data = pd.DataFrame({
        'card_id': [101, 102],
        'card_name': ['Gold', 'Platinum']
    })
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = test_data

        result = get_cards()

    assert isinstance(result, pd.DataFrame), "Функция должна возвращать DataFrame"
    assert not result.empty, "DataFrame не должен быть пустым"
    assert list(result.columns) == ['card_id', 'card_name'], "Неверные колонки"


def test_get_cards_info():
    """Проверка основной логики функции"""
    test_data = pd.DataFrame({
        "Номер карты": ["1234567890123456", "9876543210987654", "1234567890123456"],
        "Сумма операции": [-1000, -500, -200]
    })
    result = get_cards_info(test_data)

    # Проверка первой карты
    assert len(result) == 2
    assert result[0]["last_digits"] == "3456"
    assert result[0]["total_spent"] == 1200
    assert result[0]["cashback"] == 12.00

    # Проверка второй карты
    assert result[1]["last_digits"] == "7654"
    assert result[1]["total_spent"] == 500
    assert result[1]["cashback"] == 5.0


def test_get_top_five_max_prices():
    """Проверяем сортировку по убыванию и выбор топ-5"""
    test_data = pd.DataFrame({
        "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"],
        "Сумма платежа": [100, 500, 300, 700, 200, 900],
        "Категория": ["Еда", "Транспорт", "Кафе", "Техника", "Кино", "Одежда"],
        "Описание": ["Магазин", "Такси", "Кофе", "Наушники", "Билет", "Куртка"]
    })

    result = get_top_five_max_prices(test_data)

    assert len(result) == 5
    assert result[0]["amount"] == 900
    assert result[1]["amount"] == 700
    assert result[2]["amount"] == 500
    assert result[3]["amount"] == 300
    assert result[4]["amount"] == 200


def test_get_api_currency():
    """ Тест успешного получения курса валют"""
    test_data = {
        "rates": {"RUB": 75.50},
        "success": True
    }
    mock_responce = Mock()
    mock_responce.json.return_value = test_data

    with patch("requests.get", return_value=mock_responce), \
        patch.dict('os.environ', {'API_KEY_FOR_CURRENCY': 'test-key'}):

        result = get_api_currency("USD")

        assert result == 75.50


def test_get_api_stocks():
    """ Тест успешного получения данных об акции"""
    test_data = {
        "price": "150.25",
        "symbol": "AAPL"
    }
    mock_responce = Mock()
    mock_responce.json.return_value = test_data

    with patch("requests.get", return_value=mock_responce), \
        patch.dict('os.environ', {'API_KEY_FOR_CURRENCY': 'test-key'}):

        result = get_api_stocks("AAPL")

        assert result == test_data
