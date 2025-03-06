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
        self.app_data_path = os.path.join(os.getenv('APPDATA'), 'Techforge')
        self.machine_file = os.path.join(self.app_data_path, 'machine.json')
        self.key_b = Fernet.generate_key()  # Chave para encriptação local
        self.fernet_b = Fernet(self.key_b)
        
        # Garante que o diretório existe
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)

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
            worksheet = sheet.add_worksheet(title='Serial', rows="1000", cols="2")
            # Adiciona cabeçalho
            worksheet.append_row(["Machine ID", "Key"])
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

    def register_machine(self):
        try:
            machine_info = self._get_machine_info()
            if not machine_info:
                return False
            
            # Gera chave A para planilha
            key_a = Fernet.generate_key()
            fernet_a = Fernet(key_a)
            
            # Encripta o ID e informações
            encrypted_a = fernet_a.encrypt(json.dumps(machine_info).encode()).decode()
            encrypted_b = self.fernet_b.encrypt(json.dumps(machine_info).encode()).decode()
            
            # Salva na planilha
            worksheet = self._get_serial_worksheet()
            
            # Garante que tem o cabeçalho correto
            if worksheet.row_values(1) != ["Machine Info", "Key", "Hostname", "Last IP", "Added Date"]:
                worksheet.clear()
                worksheet.append_row(["Machine Info", "Key", "Hostname", "Last IP", "Added Date"])
            
            # Adiciona a nova máquina
            new_row = [
                encrypted_a,           # Machine Info (encrypted)
                key_a.decode(),       # Key
                machine_info['hostname'], # Hostname
                machine_info['ip'],      # Last IP
                machine_info['date_added'] # Added Date
            ]
            worksheet.append_row(new_row)
            
            # Salva localmente
            machine_data = {
                "machine_info": encrypted_b,
                "key": self.key_b.decode(),
                "details": machine_info
            }
            
            with open(self.machine_file, 'w') as f:
                json.dump(machine_data, f)
            
            return True
            
        except Exception as e:
            logger_app.log_error(f"Erro ao registrar máquina: {str(e)}")
            return False

    def is_machine_authorized(self, is_admin_a5=False):
        if is_admin_a5:
            return True
            
        try:
            # Carrega dados locais
            with open(self.machine_file, 'r') as f:
                machine_data = json.load(f)
            
            # Obtem informações da máquina atual
            local_machine_info = self._get_machine_info()
            if not local_machine_info:
                return False
                
            # Carrega dados da planilha
            worksheet = self._get_serial_worksheet()
            registered_machines = worksheet.get_all_values()
            
            # Remove cabeçalho
            if len(registered_machines) > 0 and registered_machines[0][0] == "Machine Info":
                registered_machines = registered_machines[1:]
            
            # Verifica cada máquina registrada
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
            all_values = worksheet.get_all_values()
            
            # Verifica se tem o cabeçalho correto
            expected_header = ["Machine Info", "Key", "Hostname", "Last IP", "Added Date"]
            if not all_values or all_values[0] != expected_header:
                # Se não tiver cabeçalho ou estiver errado, adiciona
                worksheet.clear()
                worksheet.append_row(expected_header)
                all_values = [expected_header]
            
            # Remove o cabeçalho e filtra linhas vazias
            data_rows = all_values[1:]
            
            # Filtra apenas linhas com dados válidos (5 colunas)
            valid_rows = []
            for row in data_rows:
                if len(row) == 5 and all(col.strip() for col in row):
                    valid_rows.append(row)
                
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
