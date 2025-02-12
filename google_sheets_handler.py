#google_sheets_handler.py

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

from constants import GOOGLE_SHEETS_SCOPE
import logger_app

def api_call_handler(func):
    def wrapper(*args, **kwargs):
        for i in range(0, 10):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger_app.log_error(f"API call failed: {str(e)}")
                time.sleep(2 ** i)
        error_msg = "The program couldn't connect to the Google Spreadsheet API for 10 times. Give up and check it manually."
        logger_app.log_error(error_msg)
        raise SystemError(error_msg)
    return wrapper

class GoogleSheetsHandler:
    def __init__(self, credentials_file, sheet_url):
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, GOOGLE_SHEETS_SCOPE)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_url(sheet_url).sheet1
        self.email_sheet = self.client.open_by_url(sheet_url).worksheet('Email')

        self.column_indices = {name: idx + 1 for idx, name in enumerate(self.sheet.row_values(1))}

    @api_call_handler
    def load_data(self):
        records = self.sheet.get_all_records()
        return pd.DataFrame(records)

    @api_call_handler
    def update_status(self, timestamp_value, new_status, user_name=None):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                self.sheet.update_cell(row_number, self.column_indices['Status'], new_status)
                current_timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'Ultima modificação' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['Ultima modificação'], user_name)

                # Obtém o ID da solicitação
                id_value = self.sheet.cell(row_number, self.column_indices.get('Id', 1)).value
                
                # Log incluindo o ID da solicitação
                logger_app.log_info(f"update_status: {user_name} mudou status para {new_status}, ID={id_value}, timestamp={timestamp_value}")
                return True
        return False

    @api_call_handler
    def update_value(self, timestamp_value, new_value, user_name=None):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                self.sheet.update_cell(row_number, self.column_indices['Valor'], new_value)
                current_timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'Ultima modificação' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['Ultima modificação'], user_name)

                
                # Obtém o ID da solicitação
                id_value = self.sheet.cell(row_number, self.column_indices.get('Id', 1)).value
                
                logger_app.log_info(f"update_value: {user_name} alterou valor para {new_value}, ID={id_value}, timestamp={timestamp_value}")
                return True
        return False

    @api_call_handler
    def update_cell(self, timestamp_value, column_name, new_value):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                if column_name in self.column_indices:
                    col_number = self.column_indices[column_name]
                    self.sheet.update_cell(row_number, col_number, new_value)
                    return True
        return False

    @api_call_handler
    def update_observations(self, timestamp_value, observations):
        """Atualiza as observações de uma solicitação específica."""
        try:
            cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
            for idx, cell_value in enumerate(cell_list[1:], start=2):
                if cell_value == timestamp_value:
                    row_number = idx
                    if 'Observações' in self.column_indices:
                        col_number = self.column_indices['Observações']
                        self.sheet.update_cell(row_number, col_number, observations)
                        logger_app.log_info(f"update_observations: Observações atualizadas para timestamp={timestamp_value}")
                        return True
            return False
        except Exception as e:
            logger_app.log_error(f"Erro ao atualizar observações: {e}")
            return False

    @api_call_handler
    def get_notification_emails(self):
        """Retorna um dicionário com os emails para cada tipo de notificação"""
        try:
            data = self.email_sheet.get_all_records()
            if not data:
                logger_app.log_warning("Planilha de emails vazia")
                return {}
                
            row_data = data[0]
            emails_dict = {}
            
            for key in ["AguardandoAprovacao", "Pendencias", "ProntoPagamento", "Cancelado", "Autorizado"]:
                email_str = row_data.get(key, "")
                if isinstance(email_str, str):
                    # Filtra emails vazios e remove espaços em branco
                    emails = [e.strip() for e in email_str.split(",") if e.strip()]
                    emails_dict[key] = emails
                else:
                    emails_dict[key] = []
                
                logger_app.log_info(f"Emails carregados para {key}: {emails_dict[key]}")
                    
            return emails_dict
        except Exception as e:
            logger_app.log_error(f"Erro ao obter emails de notificação: {str(e)}")
            return {}

    @api_call_handler
    def update_notification_emails(self, column, emails):
        """Atualiza os emails de notificação para uma coluna específica"""
        try:
            # Encontra o índice da coluna
            header = self.email_sheet.row_values(1)
            if column not in header:
                return False
            
            col_idx = header.index(column) + 1
            
            # Junta os emails com vírgula
            email_str = ",".join(emails)
            
            # Atualiza a célula
            self.email_sheet.update_cell(2, col_idx, email_str)
            return True
        except Exception as e:
            logger_app.log_error(f"Erro ao atualizar emails de notificação: {e}")
            return False
