import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import logging
import os

# URL da planilha de logs
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/15_0ArdsS89PRz1FmMmpTU9GQzETnUws6Ta-_TNCWITQ/edit?usp=sharing"

# Nome das abas (worksheets) para os logs
INFO_SHEET_NAME = "Info"
ERROR_SHEET_NAME = "Errors"

# Configuração do escopo e credenciais para acesso à API do Google Drive/Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_file = "credentials.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
client = gspread.authorize(creds)

# Abre a planilha pelo URL
spreadsheet = client.open_by_url(SPREADSHEET_URL)

def get_or_create_worksheet(sheet_name):
    """
    Tenta obter a worksheet com o nome sheet_name.
    Se ela não existir, cria-a e adiciona um cabeçalho padrão.
    """
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
        # Adiciona cabeçalho para identificação dos registros
        worksheet.append_row(["Timestamp", "Level", "Message"])
    return worksheet

# Obter (ou criar) as worksheets para os logs
info_sheet = get_or_create_worksheet(INFO_SHEET_NAME)
error_sheet = get_or_create_worksheet(ERROR_SHEET_NAME)

def setup_logger():
    log_path = os.path.join(os.getcwd(), 'app.log')
    if not os.path.exists(log_path):
        with open(log_path, 'a') as f:
            pass
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )


def append_log(worksheet, level, message):
    """
    Adiciona uma nova linha à worksheet informada contendo o timestamp, o nível e a mensagem.
    """
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    worksheet.append_row([timestamp, level, message])

def log_info(message):
    """
    Registra uma mensagem de nível INFO na aba "Info".
    """
    append_log(info_sheet, "INFO", message)

def log_warning(message):
    """
    Registra uma mensagem de nível WARNING na aba "Info".
    
    """
    append_log(info_sheet, "WARNING", message)

def log_error(message):
    """
    Registra uma mensagem de nível ERROR na aba "Errors".
    """
    append_log(error_sheet, "ERROR", message)
