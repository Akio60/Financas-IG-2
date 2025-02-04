# logger_app.py

import logging
import os
import hashlib

def setup_logger():
    log_path = os.path.join(os.getcwd(), 'app.log')
    # Cria o arquivo se não existir
    if not os.path.exists(log_path):
        with open(log_path, 'a') as f:
            pass
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)
