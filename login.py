# login.py

import tkinter as tk
from tkinter import Canvas, Entry, Button, PhotoImage, messagebox
from pathlib import Path

# IMPORTANTE:
# Se estiver usando ttkbootstrap, você pode substituir tkinter por ttkbootstrap.
# Caso contrário, mantenha tkinter puro como gerado pelo Tkinter Designer.

# Simulação de "banco de dados" com 3 cargos
USERS_DB = {
    "admin":    {"password": "admin123",    "role": "ADMIN"},
    "finance":  {"password": "fin123",      "role": "FINANCE"},
    "user":     {"password": "user123",     "role": "USER"}
}

# Ajuste o caminho das imagens, de acordo com a pasta gerada
# no seu Figma / Tkinter Designer
ASSETS_PATH = Path(r"C:\Users\Vitor Akio\Desktop\Teste figma\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class LoginWindow:
    """
    Classe que representa a tela de Login.
    Ao autenticar com sucesso, armazenamos o 'role' (cargo) e destruímos a janela,
    retornando-o para uso no aplicativo principal.
    """
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("862x519")
        self.window.configure(bg = "#3A7FF6")
        self.window.title("Tela de Login")

        self.role = None  # Aqui será armazenado o cargo do usuário logado

        self._build_ui()

    def _build_ui(self):
        # Código gerado pelo Tkinter Designer (adapte se precisar)
        self.canvas = Canvas(
            self.window,
            bg = "#3A7FF6",
            height = 519,
            width = 862,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            425.9999999999999,
            1.999999999999993,
            862.9999999999999,
            523.0,
            fill="#FCFCFC",
            outline=""
        )
        self.canvas.create_rectangle(
            52.999999999999886,
            91.0,
            197.9999999999999,
            96.0,
            fill="#FCFCFC",
            outline=""
        )

        # Botão "Login"
        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        self.button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self._attempt_login,  # Ao clicar, chamamos _attempt_login
            relief="flat"
        )
        self.button_1.image = button_image_1
        self.button_1.place(x=556.9999999999999, y=361.0, width=180.0, height=55.0)

        # Campo "Senha"
        entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(654.5, 285.0, image=entry_image_1)
        self.entry_image_1 = entry_image_1
        self.entry_pass = Entry(
            bd=0,
            bg="#B1CBFA",
            fg="#000716",
            highlightthickness=0,
            font=("Roboto Bold", 20),
            show="*"  # Oculta a senha
        )
        self.entry_pass.place(x=494, y=258, width=321, height=52)

        self.canvas.create_text(
            483, 217,
            anchor="nw",
            text="Senha:",
            fill="#505485",
            font=("Roboto Bold", 20)
        )

        # Campo "Login"
        entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(654.5, 155.0, image=entry_image_2)
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
            486, 98,
            anchor="nw",
            text="Login:",
            fill="#505485",
            font=("Roboto Bold", 20)
        )

        # Título
        self.canvas.create_text(
            28, 28,
            anchor="nw",
            text="Sistema de Gestão de \nRequerimentos de Orçamentos",
            fill="#FCFCFC",
            font=("Roboto Bold", 24)
        )
        # Subtítulo
        self.canvas.create_text(
            52.999999999999886,
            100.0,
            anchor="nw",
            text="IG - Instituto de Geociências da UNICAMP\n",
            fill="#FCFCFC",
            font=("Roboto Bold", 12)
        )

        # Texto adicional
        self.canvas.create_text(
            64.99999999999989,
            146.0,
            anchor="nw",
            text="Recebimento unificado das solicitações.\n\nSistema de visualização e gerenciamento \nem cada etapa do processo.\n\nEnvio automatizado de e-mails.\n\nEstatísticas e Gráficos.",
            fill="#FCFCFC",
            font=("CrimsonText Bold", 11)
        )
        self.canvas.create_text(
            27.999999999999886,
            428.0,
            anchor="nw",
            text="Desenvolvido por Vitor Isawa e Leonardo Macedo ...",
            fill="#FFFFFF",
            font=("Piazzolla Regular", 10)
        )
        self.canvas.create_text(
            229.9999999999999,
            462.0,
            anchor="nw",
            text="vitorakioisawa@gmail.com\nl239207@dac.unicamp.br",
            fill="#FFFFFF",
            font=("Petrona Regular", 10)
        )
        self.canvas.create_text(
            748.9999999999999,
            498.0,
            anchor="nw",
            text="ver.: 2.2.01 - distrib.: 1/02/2025",
            fill="#000000",
            font=("Rokkitt Bold", 8)
        )
        image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(112.99999999999989, 481.0, image=image_image_1)
        # Manter referência
        self.image_image_1 = image_image_1

        self.window.resizable(False, False)

    def _attempt_login(self):
        """
        Quando clicamos no botão "Login", vamos verificar
        se o usuário e senha conferem e definir o cargo (role).
        """
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        # Verifica no nosso "banco de dados"
        if user in USERS_DB:
            if USERS_DB[user]["password"] == password:
                # Login bem-sucedido
                self.role = USERS_DB[user]["role"]
                self.window.destroy()  # Fecha a tela de login
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "Usuário não encontrado!")

    def run(self):
        """
        Inicia o loop da janela de login. Ao sair, se role estiver definido,
        significa que autenticou com sucesso.
        """
        self.window.mainloop()
        return self.role

def show_login():
    """
    Função de conveniência para criar a tela de login, exibi-la e
    retornar o cargo do usuário (ou None, se não logou).
    """
    login_screen = LoginWindow()
    user_role = login_screen.run()
    return user_role
