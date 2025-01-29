import os
import sys
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from login import show_login
from google_sheets_handler import GoogleSheetsHandler
from email_sender import EmailSender
from constants import EMAIL_PASSWORD_ENV
from app.main_app import App

# Logger
import logger_app  # nossa camada de logs

def main():
    username, user_role = show_login()

    if not user_role:
        # Se user_role for None, significa que o login foi cancelado/fechado
        print("Login cancelado. Encerrando aplicativo.")
        sys.exit(0)

    # Configura logger
    logger_app.setup_logger()

    # Credenciais e URL da planilha
    credentials_file = "credentials.json"
    sheet_url = "https://docs.google.com/spreadsheets/d/1sNwhkq0nCuTMRhs2HmahV88uIn9KiXY1ex0vlOwC0O8/edit?usp=sharing"  # Ajuste p/ sua planilha

    # Ajuste a variável de ambiente com a senha do email (pseudo-hash, exemplo simples)
    raw_password = "oukz okul wlzp liwb"
    #hashed_pass = logger_app.simple_hash(raw_password)  # Exemplo "melhoria" item #5
    #os.environ[EMAIL_PASSWORD_ENV] = hashed_pass

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "exemplo@gmail.com"

    sheets_handler = GoogleSheetsHandler(credentials_file, sheet_url)
    email_sender = EmailSender(smtp_server, smtp_port, sender_email)

    root = tb.Window(themename='flatly')

    app = App(root, sheets_handler, email_sender, user_role, user_name=username)

    root.mainloop()

if __name__ == "__main__":
    main()
