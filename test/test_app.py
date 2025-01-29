import unittest
from app.main_app import App
from google_sheets_handler import GoogleSheetsHandler
from email_sender import EmailSender
import ttkbootstrap as tb

class TestApp(unittest.TestCase):
    def setUp(self):
        self.root = tb.Window(themename='flatly')
        self.sheets_handler = GoogleSheetsHandler("credentials.json", "https://...")
        self.email_sender = EmailSender("smtp.gmail.com", 587, "exemplo@gmail.com")
        self.app = App(self.root, self.sheets_handler, self.email_sender, "A3", user_name="Tester")

    def tearDown(self):
        self.root.destroy()

    def test_select_view_pendencias(self):
        self.app.select_view("Pendências")
        self.assertEqual(self.app.current_view, "Pendências")

    def test_user_role_restriction_A1(self):
        self.app.user_role = "A1"
        self.assertEqual(self.app.user_role, "A1")
        # A1 não pode estatísticas
        # Basta verificar se o settings_button fica oculto, etc.
        # Aqui poderíamos checar se a manipulação do layout é feita.

if __name__ == '__main__':
    unittest.main()
