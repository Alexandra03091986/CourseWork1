import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import spending_by_category, report_to_file


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    return pd.DataFrame({
        "Дата операции": ["01.09.2021 12:00:00", "15.10.2021 14:00:00", "25.11.2021 10:00:00"],
        "Категория": ["Дом и ремонт", "Еда", "Дом и ремонт"],
        "Сумма операции": [-5000, -300, -1500],
        "Описание": ["Покупка материалов", "Продукты", "Ремонтные работы"]
    })


@pytest.fixture
def mock_get_cards(sample_transactions):
    """Фикстура для мокирования функции get_cards"""
    with patch('src.utils.get_cards') as mock:
        mock.return_value = sample_transactions
        yield mock


def test_spending_by_category(sample_transactions, mock_get_cards):
    """ Проверяет базовую функциональность фильтрации"""
    result = spending_by_category(sample_transactions, "Дом и ремонт", "2021-11-26")
    assert len(result) == 2

    for category in result["Категория"]:
        assert category == "Дом и ремонт"

    assert all(result["Сумма операции"] < 0)


def test_spending_by_category_date_filter(sample_transactions):
    """Тест фильтрации по дате"""
    # Должна попасть только одна транзакция (25.11.2021)
    result = spending_by_category(sample_transactions, "Дом и ремонт", "2021-11-20")

    assert len(result) == 1
    assert result.iloc[0]["Дата операции"].strftime("%d.%m.%Y") == "01.09.2021"


# Тест декоратора report_to_file
def test_report_to_file_decorator(sample_transactions, tmp_path):
    """Проверяет, что декоратор сохраняет отчет в файл"""
    with patch('src.reports.PATH_DATA', tmp_path), \
            patch('src.reports.logger.info') as mock_logger:
        # Вызываем декорированную функцию
        result = spending_by_category(sample_transactions, "Дом и ремонт", "2021-11-25")

        # Проверяем, что файл был создан
        files = list(tmp_path.glob('*.json'))
        assert len(files) == 1

        # Проверяем запись в лог
        mock_logger.assert_called_once()
        assert "Отчет сохранен в файл" in mock_logger.call_args[0][0]


# Тест пустого результата
def test_spending_by_category_empty_result(sample_transactions):
    """Проверяет обработку случая, когда нет подходящих транзакций"""
    result = spending_by_category(sample_transactions, "Такси", "2021-11-25")
    assert len(result) == 0


# Тест с текущей датой
def test_spending_by_category_current_date(sample_transactions):
    """Проверяет работу функции с текущей датой"""
    with patch('src.reports.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2021, 11, 26)
        result = spending_by_category(sample_transactions, "Дом и ремонт")
        assert len(result) == 2


# Тест обработки ошибок
def test_spending_by_category_error_handling():
    """Проверяет обработку невалидных данных"""
    empty_df = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма операции", "Описание"])
    with patch('src.utils.get_cards', return_value=empty_df):
        result = spending_by_category(empty_df, "Дом и ремонт", "2021-11-26")
        assert len(result) == 0
        assert list(result.columns) == ["Дата операции", "Категория", "Сумма операции", "Описание"]

def test_report_to_file_dataframe(tmp_path, sample_transactions):
    """Тест сохранения DataFrame через декоратор"""
    with patch('src.reports.PATH_DATA', tmp_path):
        @report_to_file('test_report.json')
        def dummy_func():
            return sample_transactions

        result = dummy_func()

        # Проверяем что файл создан
        assert (tmp_path/ 'test_report.json').exists()
        # Проверяем содержимое файла
        loaded = pd.read_json(tmp_path / 'test_report.json')
        pd.testing.assert_frame_equal(sample_transactions, loaded)


def test_report_to_file_non_dataframe(tmp_path):
    """Тест сохранения не-DataFrame объекта (словаря) через декоратор"""
    test_data = {
        "key1": "value1",
        "key2": ["list", "of", "values"],
        "key3": {"nested": "dict"}
    }

    with patch('src.reports.PATH_DATA', tmp_path) as mock_logger:

        @report_to_file('non_df_report.json')
        def dummy_func():
            return test_data

        result = dummy_func()
        # Проверяем что файл создан
        file_path = tmp_path / 'non_df_report.json'
        assert file_path.exists()

        # Проверяем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == test_data

        # Проверяем что результат функции не изменен
        assert result == test_data
