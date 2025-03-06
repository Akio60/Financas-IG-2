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
        
        # Ajuste para criar diretório base do app
        self.app_data_base = os.path.join(os.getenv('APPDATA'), 'Financas-IG')
        self.app_data_path = os.path.join(self.app_data_base, 'security')
        self.machine_file = os.path.join(self.app_data_path, 'machine.json')
        
        # Cria estrutura de diretórios se não existir
        for path in [self.app_data_base, self.app_data_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    logger_app.log_error(f"Erro ao criar diretório {path}: {str(e)}")

        # Chave para encriptação local
        self.key_b = Fernet.generate_key()
        self.fernet_b = Fernet(self.key_b)

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
            worksheet = sheet.add_worksheet(title='Serial', rows="1000", cols="5")  # Alterado para 5 colunas
            # Adiciona cabeçalho correto
            worksheet.append_row(["Machine Info", "Key", "Hostname", "Last IP", "Added Date"])
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
            # Obtém informações da máquina atual
            machine_info = self._get_machine_info()
            if not machine_info:
                return False
            
            # Verifica se máquina já está registrada na planilha
            worksheet = self._get_serial_worksheet()
            registered_machines = worksheet.get_all_records(expected_headers=["Machine Info", "Key", "Hostname", "Last IP", "Added Date"])
            
            # Procura e remove registro anterior se existir
            row_index = 2  # Começa do 2 pois 1 é o cabeçalho
            for machine in registered_machines:
                if machine.get('Hostname') == machine_info['hostname']:
                    # Remove o registro antigo
                    worksheet.delete_rows(row_index)
                    break
                row_index += 1

            # Gera nova chave e encripta dados
            key_a = Fernet.generate_key()
            fernet_a = Fernet(key_a)
            
            encrypted_a = fernet_a.encrypt(json.dumps(machine_info).encode()).decode()
            encrypted_b = self.fernet_b.encrypt(json.dumps(machine_info).encode()).decode()
            
            # Adiciona novo registro na planilha
            new_row = [
                encrypted_a,           # Machine Info (encrypted)
                key_a.decode(),       # Key
                machine_info['hostname'],  # Hostname 
                machine_info['ip'],       # Last IP
                machine_info['date_added'] # Added Date
            ]
            worksheet.append_row(new_row)
            
            # Salva localmente
            machine_data = {
                "machine_info": encrypted_b,
                "key": self.key_b.decode(),
                "details": machine_info
            }
            
            try:
                with open(self.machine_file, 'w') as f:
                    json.dump(machine_data, f, indent=4)
            except Exception as e:
                logger_app.log_error(f"Erro ao salvar arquivo local: {str(e)}")
                return False

            logger_app.append_log(
                logger_app.LogLevel.INFO,
                logger_app.LogCategory.SYSTEM,
                "SYSTEM",
                "MACHINE_REGISTER",
                f"Máquina {machine_info['hostname']} registrada com sucesso"
            )
            
            return True
            
        except Exception as e:
            logger_app.log_error(f"Erro ao registrar máquina: {str(e)}")
            return False

    def _validate_machine_data(self, data):
        """Valida estrutura dos dados da máquina"""
        required_fields = ["machine_info", "key", "details"]
        detail_fields = ["hostname", "ip", "os", "username", "date_added", "machine_id"]
        
        try:
            # Verifica campos principais
            if not all(field in data for field in required_fields):
                return False
                
            # Verifica campos de detalhes
            details = data.get("details", {})
            if not all(field in details for field in detail_fields):
                return False
                
            return True
        except:
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
