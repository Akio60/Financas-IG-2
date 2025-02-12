# email_sender.py

import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox
from constants import EMAIL_PASSWORD_ENV
import logger_app

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = EMAIL_PASSWORD_ENV

    def send_email(self, recipient, subject, body):
        """
        Envio em thread para não travar a UI.
        """
        thread = threading.Thread(target=self._send_email_thread, args=(recipient, subject, body))
        thread.start()

    def _send_email_thread(self, recipient, subject, body):
        try:
            if not self.sender_password:
                raise ValueError("Senha do remetente não configurada. Verifique a variável de ambiente.")

            if not recipient or not subject or not body:
                raise ValueError("Recipient, subject e body são obrigatórios")

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = None
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, msg.as_string())
                logger_app.log_info(f"E-mail enviado com sucesso para {recipient}")
                messagebox.showinfo("Sucesso", f"E-mail enviado com sucesso para {recipient}!")
            except Exception as e:
                raise Exception(f"Erro ao enviar email: {str(e)}")
            finally:
                if server:
                    server.quit()

        except Exception as e:
            error_msg = f"Erro ao enviar e-mail: {str(e)}"
            logger_app.log_error(error_msg)
            messagebox.showerror("Erro", error_msg)
