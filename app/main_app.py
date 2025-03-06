import os
import json
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, date
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

        # Colunas customizadas (novos filtros)
        self.custom_views = {
            "Aguardando aprovação": [
                'Id', 'Carimbo de data/hora_str',
                'Nome completo (sem abreviações):','Telefone de contato:',
                'Curso:',
                'Orientador',
                'Qual a agência de fomento?',
                'Motivo da solicitação'
            ],
            "Aceitas": [
                'Id', 'Carimbo de data/hora_str','Ultima Atualizacao_str', 'Ultima modificação',
                'Nome completo (sem abreviações):','Telefone de contato:',
                'Curso:',
                'Orientador',
                'Qual a agência de fomento?',
                'Motivo da solicitação',
            ],
            "Aguardando documentos": [
                'Id','Carimbo de data/hora_str','Ultima Atualizacao_str', 'Ultima modificação',
                'Nome completo (sem abreviações):','Telefone de contato:',
                'Curso:',
                'Orientador',
                'Qual a agência de fomento?',
                'Motivo da solicitação',
            ],
            "Pronto para pagamento": [
                'Id','Carimbo de data/hora_str','Ultima Atualizacao_str', 'Ultima modificação',
                'Nome completo (sem abreviações):','Telefone de contato:',
                'Curso:',
                'Orientador',
                'Qual a agência de fomento?',
                'Motivo da solicitação',
                'Valor'
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

        self.home_button = tb.Button(
            self.left_frame,
            text="🏠 Home",
            bootstyle=PRIMARY,
            command=self.go_to_home
        )
        self.home_button.pack(pady=10, padx=10, fill=X)

        self.received_button = tb.Button(
            self.left_frame,
            text="Solicitações recebidas",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Aguardando aprovação")
        )
        self.received_button.pack(pady=10, padx=10, fill=X)

        self.accepted_button = tb.Button(
            self.left_frame,
            text="Solicitações aceitas",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Aceitas")
        )
        self.accepted_button.pack(pady=10, padx=10, fill=X)

        self.await_docs_button = tb.Button(
            self.left_frame,
            text="Solicitações aguardando documentos",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Aguardando documentos")
        )
        self.await_docs_button.pack(pady=10, padx=10, fill=X)

        self.ready_for_payment_button = tb.Button(
            self.left_frame,
            text="Solicitações esperando pagamento",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Pronto para pagamento")
        )
        self.ready_for_payment_button.pack(pady=10, padx=10, fill=X)

        bottom_buttons_frame = tb.Frame(self.left_frame)
        bottom_buttons_frame.pack(side=BOTTOM, fill=X, pady=10)

        self.settings_button = tb.Button(
            self.left_frame,
            text='⚙ Configurações',
            bootstyle=SECONDARY,
            command=self.open_settings
        )
        self.settings_button.pack(side=BOTTOM, pady=10, padx=10, fill=X)
        if self.user_role != "A5":
            self.settings_button.pack_forget()

        logout_button = tb.Button(
            bottom_buttons_frame,
            text="Logout",
            bootstyle=DANGER,
            command=self.logout
        )
        logout_button.pack(side=BOTTOM, padx=10, pady=10, fill =X)

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

        self.view_all_button = tb.Button(
            bottom_buttons_frame,
            text="Histórico de solicitações",
            bootstyle=OUTLINE,
            command=lambda: self.select_view("Todos")
        )
        self.view_all_button.pack(side=BOTTOM, pady=10, padx=10, fill=X)

        bottom_frame = tb.Frame(self.root)
        bottom_frame.pack(side=BOTTOM, fill=X)

        status_label = tb.Label(
            bottom_frame,
            text=f"Você está conectado como {self.user_name} (Cargo: {self.user_role})",
            font=("Helvetica", 10)
        )
        status_label.pack(side=LEFT, padx=10, pady=10)

        self.content_frame = tb.Frame(self.main_frame)
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.welcome_frame = tb.Frame(self.content_frame)
        self.welcome_frame.pack(fill=BOTH, expand=True)

        self.setup_welcome_screen()

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
        for btn in [self.received_button, self.accepted_button, self.await_docs_button, self.ready_for_payment_button]:
            btn.configure(bootstyle=OUTLINE)

        if view_name == "Aguardando aprovação":
            self.received_button.configure(bootstyle=PRIMARY)
        elif view_name == "Aceitas":
            self.accepted_button.configure(bootstyle=PRIMARY)
        elif view_name == "Aguardando documentos":
            self.await_docs_button.configure(bootstyle=PRIMARY)
        elif view_name == "Pronto para pagamento":
            self.ready_for_payment_button.configure(bootstyle=PRIMARY)

    def go_to_home(self):
        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None
        if self.details_frame:
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None
        if self.back_button and self.back_button.winfo_ismapped():
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

        if self.table_frame:
            self.table_frame.pack_forget()
            self.table_frame.destroy()
            self.table_frame = None

        self.go_to_home()

    def update_table(self):
        self.table_frame = tb.Frame(self.content_frame)
        self.table_frame.pack(fill=BOTH, expand=True, padx=20)

        table_title_label = tb.Label(
            self.table_frame,
            text="Controle de Orçamento IG - PPG UNICAMP",
            font=("Helvetica", 16, "bold")
        )
        table_title_label.pack(pady=10)

        style = tb.Style()
        row_height = 40
        style.configure("Treeview", rowheight=row_height, font=("TkDefaultFont", 11))

        self.tree = tb.Treeview(self.table_frame, show="headings", style="Treeview")
        self.tree.pack(fill=BOTH, expand=True)

        scrollbar = tb.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree.bind("<Double-1>", self.on_treeview_click)
        self.tree.tag_configure('oddrow', background='#f0f8ff')
        self.tree.tag_configure('evenrow', background='#ffffff')

        if self.current_view in self.custom_views:
            self.columns_to_display = self.custom_views[self.current_view]
        else:
            self.columns_to_display = [
                'Id', 'Carimbo de data/hora_str', 'Ultima Atualizacao_str', 'Ultima modificação',
                'Nome completo (sem abreviações):', 'Telefone de contato:',
                'Curso:', 'Orientador', 'Valor', 'Status'
            ]

        self.tree["columns"] = self.columns_to_display
        max_widths = {
            'Telefone de contato:': 70,
            'Ultima modificação': 55,
            'Curso:': 70,
            'Orientador':70,
            'Valor': 50,
            'Id': 50,
            'Carimbo de data/hora_str': 55,
            'Ultima Atualizacao_str': 55,
            'Motivo da solicitação': 100,
            'Qual a agência de fomento?': 70,
            'Nome completo (sem abreviações):': 250
        }
        min_widths = {
            'Telefone de contato:': 70,
            'Ultima modificação': 55,
            'Curso:': 70,
            'Orientador':70,
            'Valor': 50,
            'Id': 50,
            'Carimbo de data/hora_str': 55,
            'Ultima Atualizacao_str': 55,
            'Motivo da solicitação': 100,
            'Qual a agência de fomento?': 70,
            'Nome completo (sem abreviações):': 250
        }

        for col in self.columns_to_display:
            display_name = self.column_display_names.get(col, col)
            self.tree.heading(
                col,
                text=display_name,
                command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False)
            )
            col_width = max(max_widths.get(col, 150), min_widths.get(col, 50))
            self.tree.column(col, anchor="center", width=col_width)

        # Busca os dados atualizados da planilha
        self.data = self.sheets_handler.load_data()

        self.data['Carimbo de data/hora'] = pd.to_datetime(
            self.data['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        self.data['Carimbo de data/hora_str'] = self.data['Carimbo de data/hora'].dt.strftime('%d/%m/%Y')

        self.data['Ultima Atualizacao'] = pd.to_datetime(
            self.data['Ultima Atualizacao'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        self.data['Ultima Atualizacao_str'] = self.data['Ultima Atualizacao'].dt.strftime('%d/%m/%Y')

        if self.current_view == "Search":
            data_filtered = self.data.copy()
        elif self.current_view == "Aguardando aprovação":
            data_filtered = self.data[self.data['Status'] == '']
        elif self.current_view == "Aceitas":
            data_filtered = self.data[self.data['Status'] == 'Solicitação Aceita']
        elif self.current_view == "Aguardando documentos":
            data_filtered = self.data[self.data['Status'] == 'Aguardando documentação']
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

        # Após configurar todas as colunas e inserir os dados, ordena por ID decrescente
        if 'Id' in self.columns_to_display:
            self.treeview_sort_column(self.tree, 'Id', reverse=True)

    def treeview_sort_column(self, tv, col, reverse):
        self.sorted_column = col
        self.sort_reverse = reverse
        data_list = [(tv.set(k, col), k) for k in tv.get_children('')]
        
        # Função auxiliar para converter datas
        def convert_date(date_str):
            try:
                return datetime.strptime(date_str, '%d/%m/%Y')
            except:
                return datetime.min

        # Função melhorada para converter IDs considerando formato XXXX-YYYY
        def convert_id(id_str):
            try:
                # Remove espaços e verifica se está vazio
                if not id_str or id_str.strip() == '':
                    return -1
                
                # Separa o ID no hífen e pega a segunda parte
                parts = id_str.strip().split('-')
                if len(parts) == 2:
                    return int(parts[1].strip())  # Converte apenas a parte YYYY
                return -1  # Retorna -1 para formatos inválidos
                
            except (ValueError, TypeError, IndexError):
                return -1  # Retorna -1 para qualquer erro

        # Determinando o tipo de ordenação baseado na coluna
        if col in ['Carimbo de data/hora_str', 'Ultima Atualizacao_str']:
            data_list.sort(key=lambda x: convert_date(x[0]), reverse=reverse)
        elif col == 'Id':
            # Ordena por ID (considerando apenas parte após o hífen) e depois por data
            data_list.sort(key=lambda x: (convert_id(x[0]), convert_date(tv.set(x[1], 'Carimbo de data/hora_str'))), reverse=reverse)
        elif col == 'Valor':
            data_list.sort(key=lambda x: float(x[0].replace('R$', '').replace('.', '').replace(',', '.').strip() or 0), reverse=reverse)
        else:
            data_list.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

        # Reordenando os itens
        for index, (val, k) in enumerate(data_list):
            tv.move(k, '', index)

        # Atualizando o cabeçalho com a seta
        arrow = "▲" if reverse else "▼"
        display_name = self.column_display_names.get(col, col)
        new_text = f"{display_name} {arrow}"

        # Removendo setas de todas as colunas
        for column in tv["columns"]:
            display_name = self.column_display_names.get(column, column)
            tv.heading(column, text=display_name)

        # Adicionando seta apenas na coluna ordenada
        tv.heading(col, text=new_text)

        # Configurando o próximo clique para inverter a ordem
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def on_treeview_click(self, event):
        if self.user_role in ["A1", "A5"]:  # Modificado para incluir A5
            messagebox.showinfo("Aviso", "Este perfil não tem acesso aos detalhes.")
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
            messagebox.showinfo("Aviso", "Acesso restrito ao Administrador (A5).")
            return
        self.settings_manager.open_settings()

    def show_logs(self):
        """Abre o visualizador de logs"""
        from app.log_viewer import LogViewer
        LogViewer(self.root)
    def show_logs(self):
        """Abre o visualizador de logs"""
        from app.log_viewer import LogViewer
        LogViewer(self.root)
