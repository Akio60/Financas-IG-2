
import os
import shutil
import json
import sqlite3
from datetime import datetime
import schedule
import time
import threading
import logging
from google_sheets_handler import GoogleSheetsHandler

class BackupManager:
    def __init__(self, sheets_handler: GoogleSheetsHandler):
        self.sheets_handler = sheets_handler
        self.backup_dir = "backups"
        self.setup_backup_directory()
        
    def setup_backup_directory(self):
        """Cria estrutura de diretórios para backup"""
        directories = [
            self.backup_dir,
            f"{self.backup_dir}/sheets",
            f"{self.backup_dir}/database",
            f"{self.backup_dir}/configs"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def create_backup(self):
        """Cria backup completo do sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Backup das planilhas
            data = self.sheets_handler.load_data()
            data.to_csv(f"{self.backup_dir}/sheets/data_{timestamp}.csv")
            
            # Backup do banco de dados de auditoria
            self._backup_database(timestamp)
            
            # Backup das configurações
            self._backup_configs(timestamp)
            
            # Rotaciona backups antigos
            self._rotate_backups()
            
            logging.info(f"Backup completo criado: {timestamp}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao criar backup: {str(e)}")
            return False

    def _backup_database(self, timestamp):
        """Backup do banco de dados SQLite"""
        try:
            src = "security/audit.db"
            dst = f"{self.backup_dir}/database/audit_{timestamp}.db"
            
            if os.path.exists(src):
                shutil.copy2(src, dst)
        except Exception as e:
            logging.error(f"Erro no backup do banco de dados: {str(e)}")

    def _backup_configs(self, timestamp):
        """Backup dos arquivos de configuração"""
        config_files = [
            "email_templates.json",
            "users_db.json"
        ]
        
        for file in config_files:
            try:
                if os.path.exists(file):
                    dst = f"{self.backup_dir}/configs/{file}_{timestamp}.json"
                    shutil.copy2(file, dst)
            except Exception as e:
                logging.error(f"Erro no backup de {file}: {str(e)}")

    def _rotate_backups(self, max_backups=30):
        """Remove backups mais antigos"""
        for subdir in ['sheets', 'database', 'configs']:
            path = f"{self.backup_dir}/{subdir}"
            files = os.listdir(path)
            if len(files) > max_backups:
                files.sort()
                for f in files[:-max_backups]:
                    os.remove(os.path.join(path, f))

    def start_backup_scheduler(self):
        """Inicia o agendador de backups"""
        schedule.every().day.at("00:00").do(self.create_backup)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def restore_backup(self, timestamp):
        """Restaura um backup específico"""
        try:
            # Implementar lógica de restauração
            pass
        except Exception as e:
            logging.error(f"Erro ao restaurar backup: {str(e)}")
            return False
