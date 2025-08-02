from datetime import datetime
import os
import json
import uuid
import gspread
from cryptography.fernet import Fernet
import winreg
import logger_app

class MachineManager:
    def __init__(self, credentials_file):
        self.credentials_file = credentials_file
        self.logs_sheet_url = "https://docs.google.com/spreadsheets/d/15_0ArdsS89PRz1FmMmpTU9GQzETnUws6Ta-_TNCWITQ/edit?usp=sharing"
        self.app_data_base = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'techforge')
        self.app_data_path = os.path.join(self.app_data_base, 'security')
        self.machine_file = os.path.join(self.app_data_path, 'machine_serial.json')
        # Cria diretórios se não existir
        for path in [self.app_data_base, self.app_data_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    logger_app.log_error(f"Erro ao criar diretório {path}: {str(e)}")

    def _get_machine_id(self):
        try:
            # Tenta obter ID único do Windows
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
            machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
            return machine_guid
        except:
            # Fallback: gera UUID baseado no hardware
            return str(uuid.uuid1())

    def _get_serial_worksheet(self):
        client = gspread.service_account(filename=self.credentials_file)
        sheet = client.open_by_url(self.logs_sheet_url)
        
        try:
            worksheet = sheet.worksheet('Serial')
        except:
            worksheet = sheet.add_worksheet(title='Serial', rows="1000", cols="5")
            worksheet.append_row(["Serial Key", "Encrypted Key", "Hostname", "Last IP", "Added Date"])
        return worksheet

    def _get_machine_info(self):
        """Obtém informações detalhadas da máquina"""
        import platform
        import socket
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            os_name = platform.system()
            os_version = platform.version()
            username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
            
            return {
                'hostname': hostname,
                'ip': ip,
                'os': f"{os_name} {os_version}",
                'username': username,
                'date_added': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'machine_id': self._get_machine_id()
            }
        except Exception as e:
            logger_app.log_error(f"Erro ao obter informações da máquina: {str(e)}")
            return None

    def save_local_serial(self, serial_key, encrypted_key, hostname, ip):
        data = {
            "serial_key": serial_key,
            "encrypted_key": encrypted_key,
            "hostname": hostname,
            "ip": ip
        }
        try:
            with open(self.machine_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger_app.log_error(f"Erro ao salvar serial local: {str(e)}")

    def load_local_serial(self):
        if os.path.exists(self.machine_file):
            try:
                with open(self.machine_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger_app.log_error(f"Erro ao ler serial local: {str(e)}")
        return None

    def validate_and_register_serial(self, serial_key):
        """
        Valida a serial no Google Sheets. Se não estiver vinculada, vincula à máquina atual.
        Retorna True se autorizado, False caso contrário.
        """
        worksheet = self._get_serial_worksheet()
        all_serials = worksheet.get_all_records(expected_headers=["Serial Key", "Encrypted Key", "Hostname", "Last IP", "Added Date"])
        machine_info = self._get_machine_info()
        hostname = machine_info['hostname']
        ip = machine_info['ip']

        # Procura a serial
        for idx, row in enumerate(all_serials, start=2):
            if row['Serial Key'] == serial_key:
                if not row['Hostname']:
                    # Serial disponível, vincula à máquina atual
                    from cryptography.fernet import Fernet
                    key = Fernet.generate_key()
                    fernet = Fernet(key)
                    encrypted = fernet.encrypt(json.dumps(machine_info).encode()).decode()
                    worksheet.update_cell(idx, 2, encrypted)
                    worksheet.update_cell(idx, 3, hostname)
                    worksheet.update_cell(idx, 4, ip)
                    worksheet.update_cell(idx, 5, machine_info['date_added'])
                    self.save_local_serial(serial_key, encrypted, hostname, ip)
                    logger_app.append_log(
                        logger_app.LogLevel.INFO,
                        logger_app.LogCategory.SYSTEM,
                        "SYSTEM",
                        "SERIAL_REGISTER",
                        f"Serial {serial_key} vinculada ao host {hostname}"
                    )
                    return True
                else:
                    # Serial já vinculada
                    if row['Hostname'] == hostname and row['Last IP'] == ip:
                        # Permite acesso se for a mesma máquina
                        self.save_local_serial(serial_key, row['Encrypted Key'], hostname, ip)
                        return True
                    else:
                        return False
        # Serial não encontrada
        return False

    def is_machine_authorized(self, is_admin_a5=False):
        if is_admin_a5:
            return True
        local = self.load_local_serial()
        if not local:
            return False
        worksheet = self._get_serial_worksheet()
        all_serials = worksheet.get_all_records(expected_headers=["Serial Key", "Encrypted Key", "Hostname", "Last IP", "Added Date"])
        for row in all_serials:
            if row['Serial Key'] == local['serial_key']:
                if row['Hostname'] == local['hostname'] and row['Last IP'] == local['ip']:
                    return True
        return False

    def get_registered_machines(self):
        try:
            worksheet = self._get_serial_worksheet()
            
            # Define os cabeçalhos esperados
            expected_headers = ["Machine Info", "Key", "Hostname", "Last IP", "Added Date"]
            
            # Usa get_all_records com os cabeçalhos esperados
            records = worksheet.get_all_records(expected_headers=expected_headers)
            valid_rows = []
            
            for record in records:
                if all(field.strip() for field in record.values()):  # Verifica se nenhum campo está vazio
                    valid_rows.append([
                        record["Machine Info"],
                        record["Key"],
                        record["Hostname"],
                        record["Last IP"],
                        record["Added Date"]
                    ])
            
            return valid_rows
            
        except Exception as e:
            logger_app.log_error(f"Erro ao listar máquinas: {str(e)}")
            return []

    def remove_machine(self, row_index):
        try:
            worksheet = self._get_serial_worksheet()
            worksheet.delete_rows(row_index)
            return True
        except Exception as e:
            logger_app.log_error(f"Erro ao remover máquina: {str(e)}")
            return False
            for machine_info, key_a, hostname, ip, date in registered_machines:
                try:
                    # Tenta descriptografar com a chave da planilha
                    fernet_a = Fernet(key_a.encode())
                    decrypted_info = json.loads(fernet_a.decrypt(machine_info.encode()).decode())
                    
                    # Compara o machine_id
                    if decrypted_info['machine_id'] == local_machine_info['machine_id']:
                        return True
                except Exception as e:
                    logger_app.log_error(f"Erro ao verificar máquina: {str(e)}")
                    continue
                    
            return False
            
        except Exception as e:
            logger_app.log_error(f"Erro ao verificar autorização: {str(e)}")
            return False

    def get_registered_machines(self):
        try:
            worksheet = self._get_serial_worksheet()
            
            # Define os cabeçalhos esperados
            expected_headers = ["Machine Info", "Key", "Hostname", "Last IP", "Added Date"]
            
            # Usa get_all_records com os cabeçalhos esperados
            records = worksheet.get_all_records(expected_headers=expected_headers)
            valid_rows = []
            
            for record in records:
                if all(field.strip() for field in record.values()):  # Verifica se nenhum campo está vazio
                    valid_rows.append([
                        record["Machine Info"],
                        record["Key"],
                        record["Hostname"],
                        record["Last IP"],
                        record["Added Date"]
                    ])
            
            return valid_rows
            
        except Exception as e:
            logger_app.log_error(f"Erro ao listar máquinas: {str(e)}")
            return []

    def remove_machine(self, row_index):
        try:
            worksheet = self._get_serial_worksheet()
            worksheet.delete_rows(row_index)
            return True
        except Exception as e:
            logger_app.log_error(f"Erro ao remover máquina: {str(e)}")
            return False
