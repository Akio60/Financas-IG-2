# login.py

import tkinter as tk
from tkinter import Canvas, Entry, Button, PhotoImage, messagebox
from pathlib import Path

# Dicionário com usuários
USERS_DB = {
    "visual1":  {"password": "123", "role": "A1"},  # A1 - Visualizador
    "receb1":   {"password": "123", "role": "A2"},  # A2 - Recebimento/verificação
    "gerent1":  {"password": "123", "role": "A3"},  # A3 - Gerenciamento
    "financ1":  {"password": "123", "role": "A4"},  # A4 - Gestão Financeira
    "admin":    {"password": "admin", "role": "A5"} # A5 - Admin
}

# Ajuste para que o caminho seja relativo à pasta do arquivo login.py
# Ex.: se você tiver "assets/frame0" dentro do mesmo diretório do seu projeto,
# faça algo como:
BASE_DIR = Path(__file__).resolve().parent
ASSETS_PATH = BASE_DIR / "images" / "assets" / "frame0"
# Ajuste conforme sua estrutura real

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("862x519")
        self.window.configure(bg="#3A7FF6")
        self.window.title("Tela de Login")

        self.username = None  # Armazena o nome de usuário
        self.role = None      # Armazena o cargo (A1..A5)

        self._build_ui()

    def _build_ui(self):
        self.canvas = Canvas(
            self.window,
            bg="#3A7FF6",
            height=519,
            width=862,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_rectangle(426, 2, 863, 523, fill="#FCFCFC", outline="")
        self.canvas.create_rectangle(53, 91, 198, 96, fill="#FCFCFC", outline="")

        # Botão "Login"
        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        self.button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self._attempt_login,  # Tentativa de login
            relief="flat"
        )
        self.button_1.image = button_image_1
        self.button_1.place(x=557, y=361, width=180, height=55)

        # Campo Senha
        entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        self.canvas.create_image(654.5, 285.0, image=entry_image_1)
        self.entry_image_1 = entry_image_1
        self.entry_pass = Entry(
            bd=0,
            bg="#B1CBFA",
            fg="#000716",
            highlightthickness=0,
            font=("Roboto Bold", 20),
            show="*"
        )
        self.entry_pass.place(x=494, y=258, width=321, height=52)

        self.canvas.create_text(
            483, 217, anchor="nw",
            text="Senha:",
            fill="#505485",
            font=("Roboto Bold", 20)
        )

        # Campo Login
        entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
        self.canvas.create_image(654.5, 155.0, image=entry_image_2)
        self.entry_image_2 = entry_image_2
        self.entry_user = Entry(
            bd=0,
            bg="#B1CBFA",
            fg="#000716",
            highlightthickness=0,
            font=("Roboto Bold", 20)
        )
        self.entry_user.place(x=494, y=128, width=321, height=52)

        self.canvas.create_text(
            486, 98, anchor="nw",
            text="Login:",
            fill="#505485",
            font=("Roboto Bold", 20)
        )

        # Título e textos adicionais
        self.canvas.create_text(
            28, 28, anchor="nw",
            text="Sistema de Gestão de \nRequerimentos de Orçamentos",
            fill="#FCFCFC",
            font=("Roboto Bold", 24)
        )
        self.canvas.create_text(
            53, 100, anchor="nw",
            text="IG - Instituto de Geociências da UNICAMP\n",
            fill="#FCFCFC",
            font=("Roboto Bold", 12)
        )
        self.canvas.create_text(
            65, 146, anchor="nw",
            text="Recebimento unificado das solicitações.\n\n"
                 "Sistema de visualização e gerenciamento\n"
                 "em cada etapa do processo.\n\n"
                 "Envio automatizado de e-mails.\n\n"
                 "Estatísticas e Gráficos.",
            fill="#FCFCFC",
            font=("CrimsonText Bold", 11)
        )
        self.canvas.create_text(
            28, 428, anchor="nw",
            text="Desenvolvido por Vitor Isawa e Leonardo Macedo ...",
            fill="#FFFFFF",
            font=("Piazzolla Regular", 10)
        )
        self.canvas.create_text(
            230, 462, anchor="nw",
            text="vitorakioisawa@gmail.com\nl239207@dac.unicamp.br",
            fill="#FFFFFF",
            font=("Petrona Regular", 10)
        )
        self.canvas.create_text(
            749, 498, anchor="nw",
            text="ver.: 2.2.01 - distrib.: 1/02/2025",
            fill="#000000",
            font=("Rokkitt Bold", 8)
        )

        # Imagem adicional
        image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        self.canvas.create_image(113, 481, image=image_image_1)
        self.image_image_1 = image_image_1

        self.window.resizable(False, False)

        # Focar no primeiro campo e configurar TAB/Enter
        self.entry_user.focus_set()

        # Vincular TAB: mover foco entre entry_user e entry_pass
        self.entry_user.bind("<Tab>", self._focus_to_pass)
        self.entry_pass.bind("<Tab>", self._focus_to_user)

        # Vincular Enter: tentativa de login
        self.entry_user.bind("<Return>", lambda e: self._attempt_login())
        self.entry_pass.bind("<Return>", lambda e: self._attempt_login())
        # Ou podemos também vincular Enter no self.window

    def _focus_to_pass(self, event):
        self.entry_pass.focus_set()
        return "break"  # Impede o comportamento padrão do Tab

    def _focus_to_user(self, event):
        self.entry_user.focus_set()
        return "break"

    def _attempt_login(self):
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if user in USERS_DB:
            if USERS_DB[user]["password"] == password:
                self.username = user
                self.role = USERS_DB[user]["role"]
                self.window.destroy()
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "Usuário não encontrado!")

    def run(self):
        self.window.mainloop()
        # Retorna tupla (username, role) ou (None, None) se não logou
        return (self.username, self.role)

def show_login():
    login_screen = LoginWindow()
    username, role = login_screen.run()
    # Se username é None => login cancelado
    return (username, role)
