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
        self._notification_emails_cache = None
        self._last_cache_update = None
        self._cache_timeout = 300  # 5 minutos

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
                # Formato modificado para DD-MM-YYYY HH:mm:ss
                current_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'Ultima modificação' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['Ultima modificação'], user_name)

                # Obtém o ID da solicitação
                id_value = self.sheet.cell(row_number, self.column_indices.get('Id', 1)).value
                
                # Log incluindo o ID da solicitação
                logger_app.log_data_change(
                    user=user_name or "SYSTEM",
                    action="UPDATE_STATUS",
                    details=f"Status alterado para {new_status}, ID={id_value}, timestamp={timestamp_value}"
                )
                return True
        return False

    @api_call_handler
    def update_value(self, timestamp_value, new_value, user_name=None):
        cell_list = self.sheet.col_values(self.column_indices['Carimbo de data/hora'])
        for idx, cell_value in enumerate(cell_list[1:], start=2):
            if cell_value == timestamp_value:
                row_number = idx
                self.sheet.update_cell(row_number, self.column_indices['Valor'], new_value)
                # Formato modificado para DD-MM-YYYY HH:mm:ss
                current_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                self.sheet.update_cell(row_number, self.column_indices['Ultima Atualizacao'], current_timestamp)

                if user_name and 'Ultima modificação' in self.column_indices:
                    self.sheet.update_cell(row_number, self.column_indices['Ultima modificação'], user_name)

                
                # Obtém o ID da solicitação
                id_value = self.sheet.cell(row_number, self.column_indices.get('Id', 1)).value
                
                logger_app.log_data_change(
                    user=user_name or "SYSTEM", 
                    action="UPDATE_VALUE",
                    details=f"Valor alterado para {new_value}, ID={id_value}, timestamp={timestamp_value}"
                )
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
                        logger_app.log_data_change(
                            user="SYSTEM",
                            action="UPDATE_OBSERVATIONS",
                            details=f"Observações atualizadas para timestamp={timestamp_value}"
                        )
                        return True
            return False
        except Exception as e:
            logger_app.log_error(f"Erro ao atualizar observações: {e}")
            return False

    @api_call_handler 
    def get_notification_emails(self):
        """Retorna os emails de notificação da aba Email"""
        try:
            # Verifica se tem cache válido
            if (self._notification_emails_cache and self._last_cache_update and 
                (datetime.now() - self._last_cache_update).total_seconds() < self._cache_timeout):
                return self._notification_emails_cache

            data = self.email_sheet.get_all_records()
            if not data:
                logger_app.log_warning("Planilha de emails vazia")
                return {}
                
            # Pega primeira linha que contém os emails
            row_data = data[0] if data else {}
            emails_dict = {}
            
            # Status possíveis para notificações (incluindo ADMIN)
            status_list = [
                "AguardandoAprovacao", "Pendencias", "ProntoPagamento", 
                "Cancelado", "Solicitação Aceita", "AguardandoDocumentacao", 
                "Pago", "ADMIN"  # Adicionado ADMIN à lista
            ]
            
            for status in status_list:
                if status in row_data:
                    email_str = str(row_data[status])
                    # Limpa e valida os emails
                    emails = [e.strip() for e in email_str.split(",") if e.strip()]
                    if emails:
                        emails_dict[status] = emails
            
            # Atualiza o cache
            self._notification_emails_cache = emails_dict
            self._last_cache_update = datetime.now()
                    
            return emails_dict

        except Exception as e:
            logger_app.log_error(f"Erro ao obter emails de notificação: {str(e)}")
            return {}

    @api_call_handler
    def update_notification_emails(self, column, emails):
        """Atualiza os emails de notificação para uma coluna específica"""
        try:
            # Garante que a aba Email existe e está acessível
            try:
                header = self.email_sheet.row_values(1)
            except Exception as e:
                logger_app.log_error(f"Erro ao acessar aba Email: {str(e)}")
                return False

            # Se a coluna ADMIN não existir, cria ela
            if column == 'ADMIN' and column not in header:
                next_col = len(header) + 1
                self.email_sheet.update_cell(1, next_col, 'ADMIN')
                header.append('ADMIN')

            # Encontra índice da coluna
            if column not in header:
                logger_app.log_error(f"Coluna {column} não encontrada na aba Email")
                return False

            col_idx = header.index(column) + 1
            
            # Une os emails com vírgula
            email_str = ", ".join(emails)
            
            # Verifica se já existe algum dado na segunda linha
            try:
                row_data = self.email_sheet.row_values(2)
                if len(row_data) < col_idx:
                    # Se a linha não tiver células suficientes, atualiza a célula específica
                    self.email_sheet.update_cell(2, col_idx, email_str)
                else:
                    # Se já existir dados, atualiza a célula
                    self.email_sheet.update_cell(2, col_idx, email_str)
            except:
                # Se a segunda linha não existir, insere ela
                self.email_sheet.update_cell(2, col_idx, email_str)
            
            # Invalida o cache
            self._notification_emails_cache = None
            self._last_cache_update = None
            
            logger_app.log_info(f"Emails atualizados para {column}: {email_str}")
            return True

        except Exception as e:
            logger_app.log_error(f"Erro ao atualizar emails de notificação: {str(e)}")
            return False
