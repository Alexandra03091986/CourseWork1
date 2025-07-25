from config import PATH_XLSX
from src.services import get_simple_search
from src.utils import get_cards
from src.views import get_main_page_info

def main():
    main_page_result = get_main_page_info("2021-12-24 15:44:07")
    print(main_page_result)

    all_transactions = get_cards(PATH_XLSX)
    transactions_for_service = all_transactions.to_dict("records")
    service_resalt = get_simple_search(transactions_for_service, "Перевод")
    print(service_resalt)

if __name__ == '__main__':
    main()