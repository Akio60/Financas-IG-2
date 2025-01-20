# main.py

"""
Ponto de entrada da aplicação. Instancia os componentes e inicia a GUI.
"""

import os
import tkinter as tk

from app import App
from google_sheets_handler import GoogleSheetsHandler
from email_sender import EmailSender
from constants import EMAIL_PASSWORD_ENV

def main():
    # Ajuste conforme necessário:
    credentials_file = "credentials.json"  # seu arquivo de credenciais
    sheet_url = "https://docs.google.com/spreadsheets/d/1sNwhkq0nCuTMRhs2HmahV88uIn9KiXY1ex0vlOwC0O8/edit?usp=sharing"

    # Exemplo: configurar a variável de ambiente para a senha do email
    # Substitua 'SENHA_REAL' pela sua senha
    os.environ[EMAIL_PASSWORD_ENV] = "SENHA_REAL"

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "financas.ig.nubia@gmail.com"

    # Cria instâncias para Google Sheets e Email
    sheets_handler = GoogleSheetsHandler(credentials_file, sheet_url)
    email_sender = EmailSender(smtp_server, smtp_port, sender_email)

    # Cria janela principal
    root = tk.Tk()

    # Instancia a aplicação
    app = App(root, sheets_handler, email_sender)

    # Executa loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
