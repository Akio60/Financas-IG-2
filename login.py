import tkinter as tk
from tkinter import Canvas, Entry, PhotoImage, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import os
import json
import webbrowser

class RoundedButton(tk.Canvas):
    def __init__(
        self, parent, width=100, height=40, radius=10,
        bg_color="#ffffff", fg_color="#ffffff",
        border_color="#ffffff", border_width=1,
        text="", font=None, command=None
    ):
        super().__init__(parent, width=width, height=height,
                         bg="#ffffff", highlightthickness=0)
        self.radius = radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.border_width = border_width
        self.text_str = text
        self.font = font or ("Helvetica", 10, "bold")
        self.command = command

        self.bind("<Button-1>", self.on_click)
        self.draw_button()

    def draw_button(self):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        r = self.radius
        bw = self.border_width

        x1, y1 = bw, bw
        x2, y2 = w - bw, h - bw

        # Desenha os cantos (arcos)
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,
                        fill=self.bg_color, outline=self.bg_color)

        # Retângulos intermediários
        self.create_rectangle(x1+r, y1, x2-r, y2,
                              fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(x1, y1+r, x2, y2-r,
                              fill=self.bg_color, outline=self.bg_color)

        # Contorno
        if bw > 0:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,
                            style="arc", outline=self.border_color, width=bw)

            self.create_line(x1+r, y1, x2-r, y1, fill=self.border_color, width=bw)
            self.create_line(x1+r, y2, x2-r, y2, fill=self.border_color, width=bw)
            self.create_line(x1, y1+r, x1, y2-r, fill=self.border_color, width=bw)
            self.create_line(x2, y1+r, x2, y2-r, fill=self.border_color, width=bw)

        # Texto
        self.create_text(w//2, h//2, text=self.text_str,
                         fill=self.fg_color, font=self.font)

    def on_click(self, event):
        if self.command:
            self.command()

USERS_DB_FILE = "users_db.json"
def load_users_db():
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

USERS_DB = load_users_db()

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
ASSETS_PATH = BASE_DIR / "images" / "assets" / "login"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def load_image(filename: str):
    path = relative_to_assets(filename)
    if not path.exists():
        print(f"Imagem {filename} não encontrada em {path}")
    return PhotoImage(file=str(path))

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        # Força a opção global de fundo para todos os widgets
        self.window.option_add("*Background", "#2C3E50")
        self.window.geometry("880x520")
        self.window.configure(bg="#2C3E50")
        self.window.title("Tela de Login")
        try:
            icon_path = relative_to_assets("bitmap_UNI.ico")
            im = Image.open(str(icon_path))
            photo = ImageTk.PhotoImage(im)
            self.window.iconphoto(True, photo)
        except Exception as e:
            print(f"Erro ao carregar o ícone: {e}")
        
        self.username = None
        self.role = None

        self._build_ui()
        self.center_window()

    def center_window(self):
        self.window.update_idletasks()
        w = 880
        h = 520
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y-60}")

    def _build_ui(self):
        self.canvas = Canvas(
            self.window,
            bg="#2C3E50",  # Usa o mesmo bg definido na janela
            height=520,
            width=920,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_rectangle(426, 0, 920, 520, fill="#FCFCFC", outline="")
        self.canvas.create_rectangle(28, 100, 260, 103, fill="#FCFCFC", outline="")

        def on_login():
            self._attempt_login()

        self.login_button = RoundedButton(
            parent=self.canvas,
            width=180,
            height=55,
            radius=10,
            bg_color="#2C3E50",
            fg_color="#ffffff",
            border_color="#ffffff",
            border_width=5,
            text="Login",
            font=("Helvetica", 15, "bold"),
            command=on_login
        )
        self.login_button.place(x=557, y=361)

        entry_image_1 = load_image("entry_1.png")
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

        entry_image_2 = load_image("entry_2.png")
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
            483, 88, anchor="nw",
            text="Login:",
            fill="#505485",
            font=("Roboto Bold", 20)
        )

        self.canvas.create_text(
            28, 28, anchor="nw",
            text="Sistema de Gestão de \nRequerimentos",
            fill="#FCFCFC",
            font=("Roboto Bold", 20)
        )
        self.canvas.create_text(
            28, 145, anchor="nw",
            text="IG - Instituto de Geociências da UNICAMP\n",
            fill="#FCFCFC",
            font=("Roboto Bold", 14)
        )
        self.canvas.create_text(
            65, 200, anchor="nw",
            text="Recebimento unificado das solicitações.\n\n"
                 "Sistema de visualização e gerenciamento\n"
                 "em cada etapa do processo.\n\n"
                 "Envio automatizado de e-mails.\n\n"
                 "Estatísticas e Gráficos.",
            fill="#FCFCFC",
            font=("CrimsonText Bold", 11)
        )
        self.canvas.create_text(
            28, 430, anchor="nw",
            text="Desenvolvido por Vitor Isawa e Leonardo Macedo, para mais informações\n"
                 "sobre o projeto , acesse os links abaixo ou entre em contato no e-mail:",
            fill="#FFFFFF",
            font=("Piazzolla Regular", 11 * -1)
        )
        self.canvas.create_text(
            230, 465, anchor="nw",
            text="vitorakioisawa@gmail.com\nl239207@dac.unicamp.br",
            fill="#FFFFFF",
            font=("Petrona Regular", 10)
        )
        self.canvas.create_text(
            720, 498, anchor="nw",
            text="ver.: 2.3.03 - distrib.: 1/02/2025",
            fill="#000000",
            font=("Rokkitt Bold", 8)
        )

        image_image_1 = load_image("image_1.png")
        self.hyperlink_label = tk.Label(
            self.canvas,
            image=image_image_1,
            bg="#2C3E50",
            cursor="hand2"
        )
        self.hyperlink_label.image = image_image_1
        self.hyperlink_label.place(x=90, y=465)

        def open_link(event=None):
            webbrowser.open("https://github.com/Akio60/Financas-IG-2", new=1)

        self.hyperlink_label.bind("<Button-1>", open_link)

        self.window.resizable(False, False)
        self.entry_user.focus_set()
        self.entry_user.bind("<Return>", lambda e: self._attempt_login())
        self.entry_pass.bind("<Return>", lambda e: self._attempt_login())

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
        if self.username is None:
            return (None, None)
        return (self.username, self.role)

def show_login():
    login_screen = LoginWindow()
    username, role = login_screen.run()
    return (username, role)
