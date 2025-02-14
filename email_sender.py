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

            # Converte o body para HTML com formatação melhorada
            html_body = (
                f'<html>'
                f'<body style="font-family: Arial, sans-serif; line-height: 1.6;">'
                f'<div style="max-width: 600px; margin: 0 auto; padding: 20px;">'
                f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">'
                f'{body.replace(chr(10), "<br>")}'
                f'</div>'
                f'<div style="margin-top: 20px; font-size: 12px; color: #6c757d;">'
                f'<p>Este é um email automático do Sistema Financeiro IG-UNICAMP.</p>'
                f'</div>'
                f'</div>'
                f'</body>'
                f'</html>'
            )
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html'))

            server = None
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, msg.as_string())
                logger_app.log_email(
                    user="SYSTEM",
                    recipient=recipient,
                    subject=subject,
                    status="SUCCESS"
                )
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
