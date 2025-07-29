from config import PATH_XLSX
from src.reports import spending_by_category
from src.services import get_search_for_transfers_to_individuals
from src.utils import get_cards
from src.views import get_main_page_info


def main():
    # Веб-страницы: Страница «Главная»
    main_page_result = get_main_page_info("2021-12-24 15:44:07")
    print(main_page_result)

    # Сервисы: Поиск переводов физическим лицам
    all_transactions = get_cards(PATH_XLSX)
    transactions_for_service = all_transactions.to_dict("records")

    service_resalt = get_search_for_transfers_to_individuals(transactions_for_service, "Перевод")
    print(service_resalt)

    # Отчеты: Траты по категории
    report_result = spending_by_category(all_transactions, "Дом и ремонт", "2021-11-25")
    print(report_result)


if __name__ == '__main__':
    main()
