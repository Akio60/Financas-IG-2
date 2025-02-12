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

                # Logamos a mudança
                logger_app.log_info(f"update_status: {user_name} mudou status para {new_status}, timestamp={timestamp_value}")
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

                logger_app.log_info(f"update_value: {user_name} alterou valor para {new_value}, timestamp={timestamp_value}")
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
