import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from constants import GOOGLE_SHEETS_SCOPE
import logger_app

class GoogleSheetsHandler:
    def __init__(self, credentials_file, sheet_url):
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, GOOGLE_SHEETS_SCOPE)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_url(sheet_url).sheet1

        self.column_indices = {name: idx + 1 for idx, name in enumerate(self.sheet.row_values(1))}

    def load_data(self):
        records = self.sheet.get_all_records()
        return pd.DataFrame(records)

    def update_status(self, timestamp_value, new_status, user_name=None):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                self.sheet.update_cell(row_number, self.column_indices['Status'], new_status)
                current_timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'UltimoUsuario' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['UltimoUsuario'], user_name)

                # Logamos a mudança
                logger_app.log_info(f"update_status: {user_name} mudou status para {new_status}, timestamp={timestamp_value}")
                return True
        return False

    def update_value(self, timestamp_value, new_value, user_name=None):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                self.sheet.update_cell(row_number, self.column_indices['Valor'], new_value)
                current_timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'UltimoUsuario' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['UltimoUsuario'], user_name)

                logger_app.log_info(f"update_value: {user_name} alterou valor para {new_value}, timestamp={timestamp_value}")
                return True
        return False

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
