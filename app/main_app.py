import os
import json
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import messagebox, BOTH, LEFT, Y, RIGHT, X, END
import sys

from constants import (
    ALL_COLUMNS_DETAIL, ALL_COLUMNS, BG_COLOR, BUTTON_BG_COLOR, FRAME_BG_COLOR,
    STATUS_COLORS, COLUMN_DISPLAY_NAMES
)
from google_sheets_handler import GoogleSheetsHandler
from email_sender import EmailSender

from .details_manager import DetailsManager
from .statistics_manager import StatisticsManager
from .settings_manager import SettingsManager

class App:
    def __init__(self, root, sheets_handler: GoogleSheetsHandler, email_sender: EmailSender, user_role, user_name):
        self.root = root
        self.sheets_handler = sheets_handler
        self.email_sender = email_sender
        self.user_role = user_role
        self.user_name = user_name

        # Carrega DF
        self.data = self.sheets_handler.load_data()

        # Variáveis de controle
        self.detail_columns_to_display = ALL_COLUMNS_DETAIL.copy()
        self.columns_to_display = []
        self.detail_widgets = {}
        self.current_row_data = None
        self.selected_button = None
        self.details_frame = None
        self.statistics_frame = None
        self.history_tree_data = None
        self.value_entry = None
        self.current_view = None
        self.treeview_data = None
        self.email_templates = {}

        # Cores
        self.bg_color = BG_COLOR
        self.button_bg_color = BUTTON_BG_COLOR
        self.frame_bg_color = FRAME_BG_COLOR
        self.status_colors = STATUS_COLORS
        self.column_display_names = COLUMN_DISPLAY_NAMES

        # Variável de busca
        self.search_var = tb.StringVar()

        # Instancia managers
        self.details_manager = DetailsManager(self)
        self.statistics_manager = StatisticsManager(self)
        self.settings_manager = SettingsManager(self)

        # Carrega templates de e-mail
        self.load_email_templates()

        # Frame principal
        self.setup_ui()

        # Este frame da tabela será criado SOB DEMANDA
        self.table_frame = None
        self.tree = None

        # Colunas customizadas
        self.custom_views = {
            "Aguardando aprovação": [
                'Carimbo de data/hora_str',
                'Endereço de e-mail',
                'Nome completo (sem abreviações):',
                'Curso:',
                'Orientador'
            ],
            "Pendências": [
                'Carimbo de data/hora_str',
                'Status',
                'Nome completo (sem abreviações):',
                'Ultima Atualizacao','UltimoUsuario',
                'Valor',
                'Curso:',
                'Orientador',
                'E-mail DAC:'
            ],
            "Pronto para pagamento": [
                'Carimbo de data/hora_str',
                'Nome completo (sem abreviações):',
                'Ultima Atualizacao','UltimoUsuario',
                'Valor',
                'Telefone de contato:',
                'E-mail DAC:',
                'Endereço completo (logradouro, número, bairro, cidade e estado)',
                'CPF:',
                'RG/RNE:',
                'Dados bancários (banco, agência e conta) '
            ]
        }

    def load_email_templates(self):
        try:
            with open('email_templates.json', 'r', encoding='utf-8') as f:
                self.email_templates = json.load(f)
        except FileNotFoundError:
            self.email_templates = {
                'Trabalho de Campo': 'Prezado(a) {Nome},\n\nPor favor, envie...',
                'Participação em eventos': 'Prezado(a) {Nome},\n\nPor favor, envie...',
                'Visita técnica': 'Prezado(a) {Nome},\n\nPor favor, envie...',
                'Outros': 'Prezado(a) {Nome},\n\nPor favor, envie...',
                'Aprovação': 'Prezado(a) {Nome},\n\nSua solicitação foi aprovada...',
                'Pagamento': 'Prezado(a) {Nome},\n\nSeu pagamento foi efetuado...'
            }

    def save_email_templates(self):
        with open('email_templates.json', 'w', encoding='utf-8') as f:
            json.dump(self.email_templates, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        self.root.title("Controle de Orçamento IG - PPG UNICAMP")
        self.root.state("zoomed")

        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Frame lateral
        self.left_frame = tb.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=LEFT, fill=Y)

        title_label = tb.Label(
            self.left_frame,
            text="Lista de Status",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=20, padx=10)

        # Botões do menu lateral
        self.home_button = tb.Button(
            self.left_frame,
            text="🏠",
            bootstyle=PRIMARY,
            command=self.go_to_home
        )
        self.home_button.pack(pady=10, padx=10, fill=X)

        self.empty_status_button = tb.Button(
            self.left_frame,
            text="Solicitações recebidas",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Aguardando aprovação")
        )
        self.empty_status_button.pack(pady=10, padx=10, fill=X)

        self.pending_button = tb.Button(
            self.left_frame,
            text="Solicitações em andamento",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Pendências")
        )
        self.pending_button.pack(pady=10, padx=10, fill=X)

        self.ready_for_payment_button = tb.Button(
            self.left_frame,
            text="Solicitações esperando pagamento",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Pronto para pagamento")
        )
        self.ready_for_payment_button.pack(pady=10, padx=10, fill=X)

        bottom_buttons_frame = tb.Frame(self.left_frame)
        bottom_buttons_frame.pack(side=BOTTOM, fill=X, pady=10)

        # Botão de configurações
        self.settings_button = tb.Button(
            self.left_frame,
            text='⚙ Configurações',
            bootstyle=SECONDARY,
            command=self.open_settings
        )
        self.settings_button.pack(side=BOTTOM, pady=10, padx=10, fill=X)
        # A1..A4 sem acesso a config
        if self.user_role in ["A1", "A2", "A3", "A4"]:
            self.settings_button.pack_forget()

        self.search_button = tb.Button(
            bottom_buttons_frame,
            text="Pesquisar",
            bootstyle=INFO,
            command=self.perform_search
        )
        self.search_button.pack(side=BOTTOM, pady=5, padx=10, fill=X)

        self.search_entry = tb.Entry(bottom_buttons_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=BOTTOM, pady=5, padx=10)

        search_label = tb.Label(bottom_buttons_frame, text="Pesquisar:")
        search_label.pack(side=BOTTOM, pady=(10, 0), padx=10, anchor='w')

        self.statistics_button = tb.Button(
            bottom_buttons_frame,
            text="Estatísticas",
            bootstyle=SUCCESS,
            command=self.show_statistics
        )
        self.statistics_button.pack(side=BOTTOM, pady=10, padx=10, fill=X)
        if self.user_role == "A1":
            self.statistics_button.pack_forget()

        self.view_all_button = tb.Button(
            bottom_buttons_frame,
            text="Histórico de solicitações",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Todos")
        )
        self.view_all_button.pack(side=BOTTOM, pady=10, padx=10, fill=X)

        # Frame inferior (rodapé)
        bottom_frame = tb.Frame(self.root)
        bottom_frame.pack(side=BOTTOM, fill=X)

        status_label = tb.Label(
            bottom_frame,
            text=f"Você está conectado como {self.user_name} (Cargo: {self.user_role})",
            font=("Helvetica", 10)
        )
        status_label.pack(side=LEFT, padx=10, pady=10)

        logout_button = tb.Button(
            bottom_frame,
            text="Logout",
            bootstyle=DANGER,
            command=self.logout
        )
        logout_button.pack(side=RIGHT, padx=10, pady=10)

        # Frame para o conteúdo principal (home, detalhes, etc.)
        self.content_frame = tb.Frame(self.main_frame)
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # Frame de boas-vindas
        self.welcome_frame = tb.Frame(self.content_frame)
        self.welcome_frame.pack(fill=BOTH, expand=True)

        self.setup_welcome_screen()

        # O table_frame será criado SÓ quando chamarmos select_view() ou perform_search()

        self.back_button = tb.Button(
            self.content_frame,
            text="Voltar",
            bootstyle=PRIMARY,
            command=self.back_to_main_view
        )

    def logout(self):
        sys.exit(0)

    def setup_welcome_screen(self):
        try:
            img_ig = Image.open('images/logo_unicamp.png')
            img_unicamp = Image.open('images/logo_ig.png')

            img_ig = img_ig.resize((100, 100), Image.LANCZOS)
            img_unicamp = img_unicamp.resize((100, 100), Image.LANCZOS)

            logo_ig = ImageTk.PhotoImage(img_ig)
            logo_unicamp = ImageTk.PhotoImage(img_unicamp)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar as imagens: {e}")
            return

        logos_frame = tb.Frame(self.welcome_frame)
        logos_frame.pack(pady=20)

        ig_label = tb.Label(logos_frame, image=logo_ig)
        ig_label.image = logo_ig
        ig_label.pack(side=LEFT, padx=10)

        unicamp_label = tb.Label(logos_frame, image=logo_unicamp)
        unicamp_label.image = logo_unicamp
        unicamp_label.pack(side=LEFT, padx=10)

        summary_text = (
            "Este aplicativo permite a visualização e gerenciamento das solicitações de auxílio financeiro "
            "do Programa de Pós-Graduação do IG - UNICAMP. Utilize os botões ao lado para filtrar e visualizar "
            "as solicitações."
        )

        summary_label = tb.Label(
            self.welcome_frame,
            text=summary_text,
            font=("Helvetica", 12),
            wraplength=600,
            justify='center'
        )
        summary_label.pack(pady=20)

    def select_view(self, view_name):
        self.current_view = view_name
        self.search_var.set('')

        # Oculta welcome frame se estiver visível
        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()

        # Se existe frame de estatísticas, oculta
        if self.statistics_frame and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()

        # Se existe frame de detalhes, destrói
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        # Se existia table_frame, destrói
        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None

        # Cria ou recria a tabela e exibe
        self.update_table()
        self.update_selected_button(view_name)

    def perform_search(self):
        self.current_view = "Search"

        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()
        if self.statistics_frame and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None

        self.update_table()

    def update_selected_button(self, view_name):
        if self.selected_button:
            self.selected_button.configure(bootstyle=OUTLINE)

        if view_name == "Aguardando aprovação":
            self.selected_button = self.empty_status_button
        elif view_name == "Pendências":
            self.selected_button = self.pending_button
        elif view_name == "Pronto para pagamento":
            self.selected_button = self.ready_for_payment_button
        elif view_name == "Todos":
            self.selected_button = self.view_all_button
        elif view_name == "Estatísticas":
            self.selected_button = self.statistics_button
        else:
            self.selected_button = None

        if self.selected_button:
            self.selected_button.configure(bootstyle=PRIMARY)

    def go_to_home(self):
        # Se table_frame existe, destruir
        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None
        # Se details_frame existe, destruir
        if self.details_frame:
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None
        if self.back_button.winfo_ismapped():
            self.back_button.pack_forget()
        if self.statistics_frame and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()

        self.welcome_frame.pack(fill=BOTH, expand=True)
        self.update_selected_button(None)
        self.search_var.set('')

    def back_to_main_view(self):
        if self.details_frame:
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        if self.back_button.winfo_ismapped():
            self.back_button.pack_forget()

        # Se table_frame existir, destruí-lo (caso queira recriar)
        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None

        # Volta para a home
        self.go_to_home()

    def update_table(self):
        """
        Cria o table_frame caso não exista, e exibe a TreeView com base no self.current_view.
        """
        self.table_frame = tb.Frame(self.content_frame)
        self.table_frame.pack(fill=BOTH, expand=True, padx=20)

        table_title_label = tb.Label(
            self.table_frame,
            text="Controle de Orçamento IG - PPG UNICAMP",
            font=("Helvetica", 16, "bold")
        )
        table_title_label.pack(pady=10)

        # Estilo para rowheight 20% maior e fonte +1
        style = tb.Style()
        default_row_height = style.lookup("Treeview", "rowheight", default=20)
        new_row_height = 40
        style.configure("Treeview", rowheight=new_row_height, font=("TkDefaultFont", 11))

        self.tree = tb.Treeview(self.table_frame, show="headings", style="Treeview")
        self.tree.pack(fill=BOTH, expand=True)

        scrollbar = tb.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree.bind("<Double-1>", self.on_treeview_click)
        self.tree.tag_configure('oddrow', background='#f0f8ff')
        self.tree.tag_configure('evenrow', background='#ffffff')

        # Determinar colunas a exibir
        if self.current_view in self.custom_views:
            self.columns_to_display = self.custom_views[self.current_view]
        else:
            if self.current_view == "Aguardando aprovação":
                self.columns_to_display = [
                    'Endereço de e-mail',
                    'Nome completo (sem abreviações):',
                    'Curso:',
                    'Orientador',
                    'Qual a agência de fomento?',
                    'Título do projeto do qual participa:',
                    'Motivo da solicitação',
                    'Local de realização do evento',
                    'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                    'Telefone de contato:'
                ]
            elif self.current_view == "Pendências":
                self.columns_to_display = [
                    'Carimbo de data/hora_str','Ultima Atualizacao', 'UltimoUsuario', 'Status', 'Nome completo (sem abreviações):',
                    'Valor', 'Curso:', 'Orientador'
                ]
            elif self.current_view == "Pronto para pagamento":
                self.columns_to_display = [
                    'Carimbo de data/hora_str', 'Ultima Atualizacao', 'UltimoUsuario', 'Nome completo (sem abreviações):',
                    'Valor', 'Telefone de contato:',
                    'Dados bancários (banco, agência e conta) '
                ]
            else:
                # "Todos" ou "Search"
                self.columns_to_display = [
                    'Carimbo de data/hora_str', 'Nome completo (sem abreviações):',
                    'Ultima Atualizacao','UltimoUsuario', 'Valor', 'Status'
                ]

        self.tree["columns"] = self.columns_to_display
        for col in self.columns_to_display:
            display_name = self.column_display_names.get(col, col)
            self.tree.heading(
                col,
                text=display_name,
                command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False)
            )
            self.tree.column(col, anchor="center", width=150)

        # Recarregar data
        self.data = self.sheets_handler.load_data()
        self.data['Carimbo de data/hora'] = pd.to_datetime(
            self.data['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        self.data['Carimbo de data/hora_str'] = self.data['Carimbo de data/hora'].dt.strftime('%d/%m/%Y')

        # Filtrar
        if self.current_view == "Search":
            data_filtered = self.data.copy()
        elif self.current_view == "Pendências":
            data_filtered = self.data[self.data['Status'].isin(['Autorizado', 'Aguardando documentação'])]
        elif self.current_view == "Aguardando aprovação":
            data_filtered = self.data[self.data['Status'] == '']
        elif self.current_view == "Pronto para pagamento":
            data_filtered = self.data[self.data['Status'] == 'Pronto para pagamento']
        else:
            data_filtered = self.data.copy()

        search_term = self.search_var.get().lower()
        if search_term:
            cols_for_search = [c for c in self.columns_to_display if c in data_filtered.columns]
            data_filtered = data_filtered[
                data_filtered[cols_for_search].apply(
                    lambda row: row.astype(str).str.lower().str.contains(search_term).any(),
                    axis=1
                )
            ]

        final_columns = list(self.columns_to_display)
        if 'Carimbo de data/hora' not in final_columns:
            final_columns.append('Carimbo de data/hora')

        try:
            data_filtered = data_filtered[final_columns]
        except KeyError as e:
            messagebox.showerror("Erro", f"Coluna não encontrada: {e}")
            return

        self.treeview_data = data_filtered.copy()

        for idx, row in data_filtered.iterrows():
            values = row[self.columns_to_display].tolist()
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            status_value = row.get('Status', '')
            status_color = self.status_colors.get(status_value, '#000000')

            self.tree.tag_configure(f'status_tag_{idx}', foreground=status_color)
            self.tree.insert(
                "", "end", iid=str(idx),
                values=values, tags=(tag, f'status_tag_{idx}')
            )

    def treeview_sort_column(self, tv, col, reverse):
        data_list = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            data_list.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y'), reverse=reverse)
        except ValueError:
            try:
                data_list.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
            except ValueError:
                data_list.sort(reverse=reverse)
        for index, (val, k) in enumerate(data_list):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def on_treeview_click(self, event):
        # A1 não acessa detalhes
        if self.user_role == "A1":
            messagebox.showinfo("Aviso", "Você (A1) não tem acesso aos detalhes.")
            return

        selected_item = self.tree.selection()
        if selected_item:
            row_index = int(selected_item[0])
            self.current_row_data = self.sheets_handler.load_data().loc[row_index]
            self.details_manager.show_details_in_place(self.current_row_data)

    def show_statistics(self):
        self.statistics_manager.show_statistics()

    def open_settings(self):
        if self.user_role != "A5":
            messagebox.showinfo("Aviso", "Acesso restrito ao admin (A5).")
            return
        self.settings_manager.open_settings()
