import logging
import os

from config import LOGS_DIR

""" Настраиваем логгер """
logger = logging.getLogger(__name__)    # my_logger
logger.setLevel(logging.DEBUG)

log_file_path = os.path.join(LOGS_DIR, "app.log")

# Создаем директорию, если ее нет
os.makedirs(LOGS_DIR, exist_ok=True)

""" Создаем хендлер для вывода в файл """
file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
