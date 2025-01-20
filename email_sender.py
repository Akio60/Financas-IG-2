# email_sender.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox

from constants import EMAIL_PASSWORD_ENV

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = os.getenv(EMAIL_PASSWORD_ENV)

    def send_email(self, recipient, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()

            messagebox.showinfo("Sucesso", "E-mail enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar o e-mail: {e}")
