import json
from datetime import datetime
import pandas as pd


def get_greetings() -> str:
    """ Приветствие в формате "???", где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в
    зависимости от текущего времени."""
    now = int(datetime.now().strftime('%H'))
    if 6 <= now < 10:
        return "Доброе утро"
    elif 10 <= now < 18:
        return "Добрый день"
    elif 18 <= now < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_cards(path='../data/operations.xlsx'):
    """ По каждой карте:vпоследние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей)."""
    df = pd.read_excel(path)
    filter_df = df[df["Сумма операции"] < 0]
    sum_group = filter_df.groupby("Номер карты")["Сумма операции"].sum()
    list_sum_group = sum_group.to_dict()
    result = []
    for k, v in list_sum_group.items():
        result.append({"last_digits": k[1:], "total_spent": v * (-1), "cashback": round(v / 100 * (-1), 2)})
    return result


def get_top_five_max_prices(path='../data/operations.xlsx'):
    """ Топ-5 транзакций по сумме платежа. """
    df = pd.read_excel(path)
    top_five = df.sort_values("Сумма платежа").head()
    top_transactions = top_five.to_dict("records")

    top_result = []
    for k in top_transactions:
        top_result.append({
            "date": k.get("Дата операции"),
            "amount": k.get("Сумма платежа"),
            "category": k.get("Категория"),
            "description": k.get("Описание")
        })
    return top_result       # красиво выведет в консоль если прописать так:
                            # json.dumps(top_result, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    # print(get_greetings())
    # print(get_cards())
    print(get_top_five_max_prices())