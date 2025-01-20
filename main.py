# main.py

import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from google_sheets_handler import GoogleSheetsHandler
from email_sender import EmailSender
from constants import EMAIL_PASSWORD_ENV
from app.main_app import App

def main():
    credentials_file = "credentials.json"
    sheet_url = "https://docs.google.com/spreadsheets/d/1sNwhkq0nCuTMRhs2HmahV88uIn9KiXY1ex0vlOwC0O8/edit?usp=sharing"

    # Exemplo: definir a variável de ambiente com a senha do email
    os.environ[EMAIL_PASSWORD_ENV] = "oukz okul wlzp liwb"

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "financas.ig.nubia@gmail.com"

    sheets_handler = GoogleSheetsHandler(credentials_file, sheet_url)
    email_sender = EmailSender(smtp_server, smtp_port, sender_email)

    # Cria a janela principal com um tema do ttkbootstrap (escolha um)
    root = tb.Window(themename='flatly')

    # Instancia a classe principal da aplicação
    app = App(root, sheets_handler, email_sender)

    root.mainloop()

if __name__ == "__main__":
    main()
