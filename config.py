import os

ROOT_DIR = os.path.dirname(__file__)    # корневой каталог
PATH_DATA = os.path.join(ROOT_DIR, "data")
PATH_XLSX = os.path.join(PATH_DATA, "operations.xlsx")
USER_SETTINGS = os.path.join(ROOT_DIR, "user_settings.json")

LOGS_DIR = os.path.join(ROOT_DIR, "logs")