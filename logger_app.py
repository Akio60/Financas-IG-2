import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
import json
from enum import Enum

# URL da planilha de logs
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/15_0ArdsS89PRz1FmMmpTU9GQzETnUws6Ta-_TNCWITQ/edit?usp=sharing"

# Nome das abas para diferentes tipos de logs
SHEETS = {
    'INFO': "Info",
    'ERROR': "Errors",
    'AUDIT': "Audit",
    'SECURITY': "Security"
}

class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    AUDIT = "AUDIT"
    SECURITY = "SECURITY"

class LogCategory(Enum):
    USER_ACTION = "USER_ACTION"
    SYSTEM = "SYSTEM"
    DATA_CHANGE = "DATA_CHANGE"
    SECURITY = "SECURITY"
    EMAIL = "EMAIL"

# Configuração do escopo e credenciais
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_file = "credentials.json"

# Variáveis globais para spreadsheet e worksheets
_spreadsheet = None
_worksheets = {}
_last_auth_time = None
_auth_timeout = 3500  # 58 minutos

def reauthorize():
    """Reconecta com o Google Sheets se necessário"""
    global _spreadsheet, _last_auth_time
    
    current_time = datetime.datetime.now()
    if (_last_auth_time is None or 
        (current_time - _last_auth_time).total_seconds() > _auth_timeout):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
            client = gspread.authorize(creds)
            _spreadsheet = client.open_by_url(SPREADSHEET_URL)
            _last_auth_time = current_time
            
            # Limpa cache de worksheets quando reautoriza
            _worksheets.clear()
        except Exception as e:
            logging.error(f"Erro ao reautorizar: {str(e)}")
            return False
    return True

def get_spreadsheet():
    """Função para obter ou criar conexão com spreadsheet"""
    if not reauthorize():
        return None
    return _spreadsheet

def get_worksheet(sheet_name):
    """Função para obter ou criar worksheet"""
    if sheet_name not in _worksheets or not reauthorize():
        try:
            spreadsheet = get_spreadsheet()
            if not spreadsheet:
                return None
            
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
                worksheet.append_row([
                    "Timestamp", "Level", "Category", "User", 
                    "Action", "Details", "IP", "Status"
                ])
            _worksheets[sheet_name] = worksheet
        except Exception as e:
            logging.error(f"Erro ao obter worksheet {sheet_name}: {e}")
            return None
    return _worksheets[sheet_name]

def setup_logger():
    """Configura o logger do sistema"""
    log_path = os.path.join(os.getcwd(), 'app.log')
    if not os.path.exists(log_path):
        with open(log_path, 'a') as f:
            pass
    
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

def append_log(level: LogLevel, category: LogCategory, user: str, action: str, 
               details: str, ip: str = "", status: str = "SUCCESS"):
    """Adiciona um novo registro de log com informações detalhadas."""
    try:
        timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Log local
        msg = f"{timestamp} [{level.value}] {category.value} - {user} - {action} - {details}"
        logging.info(msg)
        
        # Log no Google Sheets
        worksheet = get_worksheet(SHEETS[level.value])
        if worksheet:
            log_entry = [
                timestamp,
                level.value,
                category.value,
                user,
                action,
                details,
                ip,
                status
            ]
            try:
                worksheet.append_row(log_entry)
            except Exception as e:
                logging.error(f"Erro ao adicionar log no Google Sheets: {e}")
        
        return True
    except Exception as e:
        error_msg = f"Erro ao registrar log: {str(e)}"
        logging.error(error_msg)
        return False

# Funções específicas para diferentes tipos de logs
def log_user_action(user: str, action: str, details: str, status: str = "SUCCESS"):
    return append_log(
        LogLevel.INFO,
        LogCategory.USER_ACTION,
        user,
        action,
        details,
        status=status
    )

def log_data_change(user: str, action: str, details: str):
    return append_log(
        LogLevel.AUDIT,
        LogCategory.DATA_CHANGE,
        user,
        action,
        details,
    )

def log_security_event(user: str, action: str, details: str, ip: str = ""):
    return append_log(
        LogLevel.SECURITY,
        LogCategory.SECURITY,
        user,
        action,
        details,
        ip=ip
    )

def log_error(error_msg: str, user: str = "SYSTEM"):
    return append_log(
        LogLevel.ERROR,
        LogCategory.SYSTEM,
        user,
        "ERROR",
        error_msg,
        status="ERROR"
    )

def log_email(user: str, recipient: str, subject: str, status: str = "SUCCESS"):
    return append_log(
        LogLevel.INFO,
        LogCategory.EMAIL,
        user,
        "SEND_EMAIL",
        f"To: {recipient}, Subject: {subject}",
        status=status
    )

# Função para recuperar logs
def get_logs(level: LogLevel = None, category: LogCategory = None, 
             start_date: str = None, end_date: str = None, 
             user: str = None, limit: int = 1000):
    """
    Recupera logs com filtros específicos.
    Retorna uma lista de dicionários com os logs.
    """
    try:
        all_logs = []
        
        # Determina quais worksheets verificar
        if level:
            sheets_to_check = [SHEETS[level.value]]
        else:
            sheets_to_check = SHEETS.values()
        
        # Busca logs de cada worksheet
        for sheet_name in sheets_to_check:
            worksheet = get_worksheet(sheet_name)
            if not worksheet:
                continue
                
            try:
                records = worksheet.get_all_records()
            except Exception as e:
                logging.error(f"Erro ao buscar registros de {sheet_name}: {e}")
                continue
            
            # Aplica filtros
            filtered_records = []
            for record in records:
                if category and record.get('Category') != category.value:
                    continue
                if user and record.get('User') != user:
                    continue
                if start_date:
                    record_date = datetime.datetime.strptime(record['Timestamp'].split()[0], '%d/%m/%Y')
                    if record_date < datetime.datetime.strptime(start_date, '%d/%m/%Y'):
                        continue
                if end_date:
                    record_date = datetime.datetime.strptime(record['Timestamp'].split()[0], '%d/%m/%Y')
                    if record_date > datetime.datetime.strptime(end_date, '%d/%m/%Y'):
                        continue
                filtered_records.append(record)
            
            all_logs.extend(filtered_records)
        
        # Ordena por timestamp e limita quantidade
        all_logs.sort(key=lambda x: datetime.datetime.strptime(x['Timestamp'], '%d/%m/%Y %H:%M:%S'), reverse=True)
        return all_logs[:limit]
    
    except Exception as e:
        logging.error(f"Erro ao recuperar logs: {str(e)}")
        return []

def export_logs(filepath: str, format: str = 'json', **filters):
    """
    Exporta logs para um arquivo no formato especificado.
    Formatos suportados: json, csv
    """
    try:
        logs = get_logs(**filters)
        
        # Ordena por timestamp e limita quantidade
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)
        elif format == 'csv':
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
        
        return True
    
    except Exception as e:
        logging.error(f"Erro ao exportar logs: {str(e)}")
        return False
