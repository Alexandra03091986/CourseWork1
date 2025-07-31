import json
from typing import List, Dict, Any

import pytest

from src.services import get_search_for_transfers_to_individuals


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"Категория": "Перевод", "Описание": "Иван С.", "Сумма": 1000},
        {"Категория": "Еда", "Описание": "Магазин", "Сумма": 500},
        {"Категория": "Перевод", "Описание": "иван с.", "Сумма": 300},
    ]


def test_get_search_for_transfers_to_individuals_no_category(sample_transactions):
    """Проверяет случай, когда нет подходящей категории."""
    result = get_search_for_transfers_to_individuals(sample_transactions, "Мебель")
    assert json.loads(result) == []


def test_case_insensitivity(sample_transactions):
    """Проверяет регистронезависимость поиска имени, фильтрацию по категории"""
    found_transactions = get_search_for_transfers_to_individuals(sample_transactions, "Перевод")
    result = json.loads(found_transactions)
    assert len(result) == 2
    assert any("иван с." in tx["Описание"].lower() for tx in result)
    assert all("Перевод" in transaction["Категория"] for transaction in result)


def test_invalid_name_format():
    """Проверяет, что транзакции без 'Имя Ф.' не попадают в результат."""
    transaction =  [{
        "Категория": "Перевод",
        "Описание": "Без имени",
        "Сумма": 200
    }]
    result = get_search_for_transfers_to_individuals(transaction, "Перевод")
    assert json.loads(result) == []
