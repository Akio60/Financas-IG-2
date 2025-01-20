# app.py

"""
Arquivo que contém a classe principal de interface (Tkinter) e toda a lógica
para exibir, filtrar, visualizar detalhes e gerenciar as solicitações.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, Text
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from datetime import datetime

# Importações de arquivos internos
from constants import (
    ALL_COLUMNS_DETAIL, ALL_COLUMNS, BG_COLOR, BUTTON_BG_COLOR, FRAME_BG_COLOR,
    STATUS_COLORS, COLUMN_DISPLAY_NAMES
)
from email_sender import EmailSender
from google_sheets_handler import GoogleSheetsHandler


class App:
    def __init__(self, root, sheets_handler: GoogleSheetsHandler, email_sender: EmailSender):
        self.root = root
        self.sheets_handler = sheets_handler
        self.email_sender = email_sender

        # Carrega o DataFrame inicialmente
        self.data = self.sheets_handler.load_data()

        # Configurações de colunas e detalhes
        self.detail_columns_to_display = ALL_COLUMNS_DETAIL.copy()
        self.columns_to_display = []
        self.detail_widgets = {}
        self.current_row_data = None
        self.selected_button = None
        self.details_frame = None
        self.current_view = None
        self.treeview_data = None
        self.email_templates = {}

        # Carrega templates de e-mail
        self.load_email_templates()

        # Variáveis de cor
        self.bg_color = BG_COLOR
        self.button_bg_color = BUTTON_BG_COLOR
        self.frame_bg_color = FRAME_BG_COLOR
        self.status_colors = STATUS_COLORS
        self.column_display_names = COLUMN_DISPLAY_NAMES

        # Para busca
        self.search_var = tk.StringVar()

        # Inicia a interface
        self.setup_ui()

    def load_email_templates(self):
        """
        Carrega os templates de e-mail de um arquivo JSON ou define valores padrão.
        """
        try:
            with open('email_templates.json', 'r', encoding='utf-8') as f:
                self.email_templates = json.load(f)
        except FileNotFoundError:
            # Templates padrão
            self.email_templates = {
                'Trabalho de Campo': (
                    'Prezado(a) {Nome},\n\n'
                    'Por favor, envie os documentos necessários para o Trabalho de Campo.\n\n'
                    'Att,\nEquipe Financeira'
                ),
                'Participação em eventos': (
                    'Prezado(a) {Nome},\n\n'
                    'Por favor, envie os documentos necessários para a Participação em Eventos.\n\n'
                    'Att,\nEquipe Financeira'
                ),
                'Visita técnica': (
                    'Prezado(a) {Nome},\n\n'
                    'Por favor, envie os documentos necessários para a Visita Técnica.\n\n'
                    'Att,\nEquipe Financeira'
                ),
                'Outros': (
                    'Prezado(a) {Nome},\n\n'
                    'Por favor, envie os documentos necessários.\n\n'
                    'Att,\nEquipe Financeira'
                ),
                'Aprovação': (
                    'Prezado(a) {Nome},\n\n'
                    'Sua solicitação foi aprovada.\n\n'
                    'Att,\nEquipe Financeira'
                ),
                'Pagamento': (
                    'Prezado(a) {Nome},\n\n'
                    'Seu pagamento foi efetuado com sucesso.\n\n'
                    'Att,\nEquipe Financeira'
                ),
            }

    def save_email_templates(self):
        """
        Salva os templates de e-mail em um arquivo JSON.
        """
        with open('email_templates.json', 'w', encoding='utf-8') as f:
            json.dump(self.email_templates, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        """
        Cria todos os elementos da interface gráfica (Tkinter).
        """
        self.root.title("Controle de Orçamento IG - PPG UNICAMP")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.bg_color)

        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Frame esquerdo (painel de botões)
        self.left_frame = tk.Frame(self.main_frame, width=200, bg=self.frame_bg_color)
        self.left_frame.pack(side="left", fill="y")

        title_label = tk.Label(
            self.left_frame, text="Lista de Status",
            font=("Helvetica", 14, "bold"),
            bg=self.frame_bg_color
        )
        title_label.pack(pady=20, padx=10)

        # Botão Página Inicial
        self.home_button = tk.Button(
            self.left_frame, text="🏠",
            command=self.go_to_home,
            bg=self.button_bg_color
        )
        self.home_button.pack(pady=10, padx=10, fill="x")

        # Botões de visualização
        self.empty_status_button = tk.Button(
            self.left_frame,
            text="Solicitações recebidas",
            command=lambda: self.select_view("Aguardando aprovação"),
            bg=self.button_bg_color
        )
        self.empty_status_button.pack(pady=10, padx=10, fill="x")

        self.pending_button = tk.Button(
            self.left_frame,
            text="Solicitações em andamento",
            command=lambda: self.select_view("Pendências"),
            bg=self.button_bg_color
        )
        self.pending_button.pack(pady=10, padx=10, fill="x")

        self.ready_for_payment_button = tk.Button(
            self.left_frame,
            text="Solicitações pré efetuadas",
            command=lambda: self.select_view("Pronto para pagamento"),
            bg=self.button_bg_color
        )
        self.ready_for_payment_button.pack(pady=10, padx=10, fill="x")

        # Frame para botões inferiores
        bottom_buttons_frame = tk.Frame(self.left_frame, bg=self.frame_bg_color)
        bottom_buttons_frame.pack(side='bottom', fill='x', pady=10)

        # Botão Configurações (símbolo de engrenagem)
        self.settings_button = tk.Button(
            self.left_frame,
            text='⚙',
            command=self.open_settings,  # Referência ao método definido abaixo
            bg=self.button_bg_color
        )
        self.settings_button.pack(side='bottom', pady=10, padx=10, fill='x')

        # Barra de busca
        self.search_button = tk.Button(
            bottom_buttons_frame, text="Pesquisar",
            command=self.perform_search,
            bg=self.button_bg_color
        )
        self.search_button.pack(side='bottom', pady=5, padx=10, fill="x")

        self.search_entry = tk.Entry(bottom_buttons_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side='bottom', pady=5, padx=10)

        search_label = tk.Label(bottom_buttons_frame, text="Pesquisar:", bg=self.frame_bg_color)
        search_label.pack(side='bottom', pady=(10, 0), padx=10, anchor='w')

        # Botão Estatísticas
        self.statistics_button = tk.Button(
            bottom_buttons_frame,
            text="Estatísticas",
            command=self.show_statistics,
            bg=self.button_bg_color
        )
        self.statistics_button.pack(side='bottom', pady=10, padx=10, fill="x")

        # Botão para Histórico de solicitações
        self.view_all_button = tk.Button(
            bottom_buttons_frame,
            text="Histórico de solicitações",
            command=lambda: self.select_view("Todos"),
            bg=self.button_bg_color
        )
        self.view_all_button.pack(side='bottom', pady=10, padx=10, fill="x")

        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(side="bottom", fill="x")

        credits_label = tk.Label(
            bottom_frame,
            text="Desenvolvido por: Vitor Akio & Leonardo Macedo",
            font=("Helvetica", 10),
            bg=self.bg_color
        )
        credits_label.pack(side="right", padx=10, pady=10)

        # Frame direito (conteúdo principal)
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Frame inicial de boas-vindas
        self.welcome_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.welcome_frame.pack(fill="both", expand=True)

        self.setup_welcome_screen()

        # Frame para exibir a tabela de solicitações
        self.table_frame = tk.Frame(self.content_frame, bg=self.bg_color)

        self.table_title_label = tk.Label(
            self.table_frame,
            text="Controle de Orçamento IG - PPG UNICAMP",
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color
        )
        self.table_title_label.pack(pady=10)

        # Configuração da Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=self.bg_color,
            foreground="black",
            rowheight=25,
            fieldbackground=self.bg_color
        )
        style.map('Treeview', background=[('selected', '#347083')])

        self.tree = ttk.Treeview(self.table_frame, show="headings", style="Treeview")
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_treeview_click)

        # Cores alternadas nas linhas
        self.tree.tag_configure('oddrow', background='#f0f8ff')   # AliceBlue
        self.tree.tag_configure('evenrow', background='#ffffff')  # White

        # Botão "Voltar"
        self.back_button = tk.Button(
            self.content_frame,
            text="Voltar",
            command=self.back_to_main_view,
            bg=self.button_bg_color,
            fg="white",
            font=("Helvetica", 16, "bold"),
            width=20,
            height=2
        )

    def setup_welcome_screen(self):
        """
        Configura a tela de boas-vindas com logos e texto inicial.
        """
        try:
            # Ajuste o nome dos arquivos de logo conforme necessário
            img_ig = Image.open('logo_unicamp.png')
            img_unicamp = Image.open('logo_ig.png')

            img_ig = img_ig.resize((100, 100), Image.LANCZOS)
            img_unicamp = img_unicamp.resize((100, 100), Image.LANCZOS)

            logo_ig = ImageTk.PhotoImage(img_ig)
            logo_unicamp = ImageTk.PhotoImage(img_unicamp)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar as imagens: {e}")
            return

        logos_frame = tk.Frame(self.welcome_frame, bg=self.bg_color)
        logos_frame.pack(pady=20)

        ig_label = tk.Label(logos_frame, image=logo_ig, bg=self.bg_color)
        ig_label.image = logo_ig  # manter referência
        ig_label.pack(side='left', padx=10)

        unicamp_label = tk.Label(logos_frame, image=logo_unicamp, bg=self.bg_color)
        unicamp_label.image = logo_unicamp
        unicamp_label.pack(side='left', padx=10)

        summary_text = (
            "Este aplicativo permite a visualização e gerenciamento das solicitações de auxílio financeiro "
            "do Programa de Pós-Graduação do IG - UNICAMP. Utilize os botões ao lado para filtrar e visualizar "
            "as solicitações."
        )

        summary_label = tk.Label(
            self.welcome_frame,
            text=summary_text,
            font=("Helvetica", 12),
            wraplength=600,
            justify='center',
            bg=self.bg_color
        )
        summary_label.pack(pady=20)

    def select_view(self, view_name):
        """
        Controla qual "visão" ou lista de solicitações será exibida na tabela.
        """
        self.current_view = view_name

        # Esconde o frame de boas-vindas, se estiver visível
        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()

        # Esconde estatísticas, se estiver visível
        if hasattr(self, 'statistics_frame') and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()

        # Esconde detalhes, se estiver visível
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        # Garante que o frame da tabela esteja visível
        if not self.table_frame.winfo_ismapped():
            self.table_frame.pack(fill="both", expand=True)

        # Atualiza a tabela e o botão selecionado
        self.update_table()
        self.update_selected_button(view_name)

    def perform_search(self):
        """
        Realiza a pesquisa de qualquer termo digitado em self.search_var.
        """
        self.current_view = "Search"
        # Ocultar outros frames
        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()
        if hasattr(self, 'statistics_frame') and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        self.update_table()

    def update_selected_button(self, view_name):
        """
        Ajusta a cor do botão correspondente à visualização atual.
        """
        if self.selected_button:
            self.selected_button.config(bg=self.button_bg_color)

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
            self.selected_button.config(bg="#87CEFA")  # Cor diferenciada para o botão ativo

    def go_to_home(self):
        """
        Volta para a tela inicial (boas-vindas).
        """
        if self.table_frame.winfo_ismapped():
            self.table_frame.pack_forget()
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None
        if hasattr(self, 'statistics_frame') and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()

        self.welcome_frame.pack(fill="both", expand=True)
        self.update_selected_button(None)
        self.search_var.set('')

    def back_to_main_view(self):
        """
        Volta para a visualização principal da tabela, escondendo detalhes.
        """
        if self.details_frame:
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        self.back_button.pack_forget()
        self.table_frame.pack(fill="both", expand=True)

    def update_table(self):
        """
        Atualiza a Tabela (Treeview) de acordo com a `current_view`.
        Aplica filtros e pesquisas, se houver.
        """
        # Se existirem frames de detalhes ou estatísticas, escondê-los
        if self.details_frame:
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None
        if hasattr(self, 'statistics_frame') and self.statistics_frame.winfo_ismapped():
            self.statistics_frame.pack_forget()

        self.table_frame.pack(fill="both", expand=True)

        # Limpa a Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Definir colunas a exibir
        if self.current_view == "Aguardando aprovação":
            self.columns_to_display = [
                'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
                'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
                'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Telefone de contato:'
            ]
        elif self.current_view == "Pendências":
            self.columns_to_display = [
                'Carimbo de data/hora_str', 'Status', 'Nome completo (sem abreviações):',
                'Ultima Atualizacao', 'Valor', 'Curso:', 'Orientador', 'E-mail DAC:'
            ]
        elif self.current_view == "Pronto para pagamento":
            self.columns_to_display = [
                'Carimbo de data/hora_str', 'Nome completo (sem abreviações):', 'Ultima Atualizacao',
                'Valor', 'Telefone de contato:', 'E-mail DAC:',
                'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
                'RG/RNE:', 'Dados bancários (banco, agência e conta) '
            ]
        else:  # "Todos" / "Search" / etc.
            self.columns_to_display = [
                'Carimbo de data/hora_str', 'Nome completo (sem abreviações):',
                'Ultima Atualizacao', 'Valor', 'Status'
            ]

        # Configura colunas na Treeview
        self.tree["columns"] = self.columns_to_display
        for col in self.tree["columns"]:
            display_name = self.column_display_names.get(col, col)
            self.tree.heading(col, text=display_name, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))
            self.tree.column(col, anchor="center", width=150)

        # Recarregar dados completos
        self.data = self.sheets_handler.load_data()

        # Ajustar o formato de data/hora
        self.data['Carimbo de data/hora'] = pd.to_datetime(
            self.data['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        self.data['Carimbo de data/hora_str'] = self.data['Carimbo de data/hora'].dt.strftime('%d/%m/%Y')

        # Aplicar filtros
        if self.current_view == "Search":
            data_filtered = self.data.copy()
        else:
            if self.current_view == "Pendências":
                data_filtered = self.data[self.data['Status'].isin(['Autorizado', 'Aguardando documentação'])]
            elif self.current_view == "Aguardando aprovação":
                data_filtered = self.data[self.data['Status'] == '']
            elif self.current_view == "Pronto para pagamento":
                data_filtered = self.data[self.data['Status'] == 'Pronto para pagamento']
            else:
                data_filtered = self.data.copy()

        # Filtro de busca
        search_term = self.search_var.get().lower()
        if search_term:
            data_filtered = data_filtered[
                data_filtered[self.columns_to_display].apply(
                    lambda row: row.astype(str).str.lower().str.contains(search_term).any(),
                    axis=1
                )
            ]

        # Seleciona colunas
        try:
            data_filtered = data_filtered[self.columns_to_display + ['Carimbo de data/hora']]
        except KeyError as e:
            messagebox.showerror("Erro", f"Coluna não encontrada: {e}")
            return

        self.treeview_data = data_filtered.copy()

        # Inserir dados na Treeview
        for idx, row in data_filtered.iterrows():
            values = row[self.columns_to_display].tolist()
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            status_value = row.get('Status', '')
            status_color = self.status_colors.get(status_value, '#000000')

            self.tree.tag_configure(f'status_tag_{idx}', foreground=status_color)
            self.tree.insert("", "end", iid=str(idx), values=values, tags=(tag, f'status_tag_{idx}'))

        self.back_button.pack_forget()
        self.table_title_label.config(text="Controle de Orçamento IG - PPG UNICAMP")

    def treeview_sort_column(self, tv, col, reverse):
        """
        Ordena a coluna clicada (por data ou valor numérico ou string).
        """
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
        """
        Exibe os detalhes da linha ao dar duplo clique na Treeview.
        """
        selected_item = self.tree.selection()
        if selected_item:
            row_index = int(selected_item[0])
            self.current_row_data = self.sheets_handler.load_data().loc[row_index]
            self.show_details_in_place(self.current_row_data)

    def show_details_in_place(self, row_data):
        """
        Mostra os detalhes em abas (Notebook) dentro da mesma janela,
        substituindo o frame da tabela pela visualização de detalhes.
        """
        # Esconde a tabela
        self.table_frame.pack_forget()

        self.details_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.details_frame.pack(fill="both", expand=True)

        # Título
        self.details_title_label = tk.Label(
            self.details_frame,
            text="Controle de Orçamento IG - PPG UNICAMP",
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color
        )
        self.details_title_label.pack(pady=10)

        self.detail_widgets = {}

        # Notebook
        notebook_style = ttk.Style()
        notebook_style.theme_use('default')
        notebook_style.configure("CustomNotebook.TNotebook", background=self.bg_color)
        notebook_style.configure("CustomNotebook.TNotebook.Tab", background=self.bg_color, font=("Helvetica", 13))
        notebook_style.configure('Custom.TFrame', background=self.bg_color)
        notebook_style.configure("CustomBold.TLabel", font=("Helvetica", 12, "bold"), background=self.bg_color)
        notebook_style.configure("CustomRegular.TLabel", font=("Helvetica", 12), background=self.bg_color)

        notebook = ttk.Notebook(self.details_frame, style="CustomNotebook.TNotebook")
        notebook.pack(fill='both', expand=True)

        # Agrupar campos em seções
        sections = {
            "Informações Pessoais": [
                'Nome completo (sem abreviações):',
                'Endereço de e-mail',
                'Telefone de contato:',
                'CPF:',
                'RG/RNE:',
                'Endereço completo (logradouro, número, bairro, cidade e estado)'
            ],
            "Informações Acadêmicas": [
                'Ano de ingresso o PPG:',
                'Curso:',
                'Orientador',
                'Possui bolsa?',
                'Qual a agência de fomento?',
                'Título do projeto do qual participa:',
            ],
            "Detalhes da Solicitação": [
                'Motivo da solicitação',
                'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
                'Local de realização do evento',
                'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias (para transporte, hospedagem e alimentação), passagem aérea, pagamento de análises e traduções, etc.\n',
            ],
            "Informações Financeiras": [
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        for section_name, fields in sections.items():
            tab_frame = ttk.Frame(notebook, style='Custom.TFrame')
            notebook.add(tab_frame, text=section_name)

            tab_frame.columnconfigure(0, weight=1, minsize=200)
            tab_frame.columnconfigure(1, weight=3)

            row_idx = 0
            for col in fields:
                if col in row_data:
                    label = ttk.Label(tab_frame, text=f"{col}:", style="CustomBold.TLabel", wraplength=200, justify='left')
                    label.grid(row=row_idx, column=0, sticky='nw', padx=10, pady=5)
                    value = ttk.Label(tab_frame, text=str(row_data[col]), style="CustomRegular.TLabel", wraplength=600, justify="left")
                    value.grid(row=row_idx, column=1, sticky='nw', padx=10, pady=5)
                    self.detail_widgets[col] = {'label': label, 'value': value, 'tab_frame': tab_frame}
                    row_idx += 1

            # Caso a solicitação ainda não tenha status definido, exibir campos para autorizar/recusar
            if section_name == "Informações Financeiras" and row_data['Status'] == '':
                value_label = ttk.Label(tab_frame, text="Valor (R$):", style="CustomBold.TLabel")
                value_label.grid(row=row_idx, column=0, sticky='w', padx=10, pady=5)
                value_entry = ttk.Entry(tab_frame, width=50)
                value_entry.grid(row=row_idx, column=1, sticky='w', padx=10, pady=5)
                self.value_entry = value_entry

                row_idx += 1

                def autorizar_auxilio():
                    new_value = self.value_entry.get().strip()
                    if not new_value:
                        messagebox.showwarning("Aviso", "Por favor, insira um valor antes de autorizar o auxílio.")
                        return
                    new_status = 'Autorizado'
                    timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                    self.sheets_handler.update_status(timestamp_str, new_status)
                    self.sheets_handler.update_value(timestamp_str, new_value)
                    self.ask_send_email(row_data, new_status, new_value)
                    self.update_table()
                    self.back_to_main_view()

                def negar_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                        self.sheets_handler.update_status(timestamp_str, new_status)
                        self.ask_send_email(row_data, new_status)
                        self.update_table()
                        self.back_to_main_view()

                button_width = 25
                autorizar_button = tk.Button(
                    tab_frame,
                    text="Autorizar Auxílio",
                    command=autorizar_auxilio,
                    bg="green",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                negar_button = tk.Button(
                    tab_frame,
                    text="Recusar/Cancelar Auxílio",
                    command=negar_auxilio,
                    bg="red",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )

                autorizar_button.grid(row=row_idx, column=0, padx=10, pady=10, sticky='w')
                negar_button.grid(row=row_idx, column=1, padx=10, pady=10, sticky='w')

        # Se o status for Pendências ou Pronto para pagamento, criar aba "Ações"
        if self.current_view in ["Pendências", "Pronto para pagamento"]:
            actions_tab = ttk.Frame(notebook, style='Custom.TFrame')
            notebook.add(actions_tab, text="Ações")

            if self.current_view == "Pendências":
                def request_documents():
                    new_status = 'Aguardando documentação'
                    timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                    self.sheets_handler.update_status(timestamp_str, new_status)

                    motivo = row_data.get('Motivo da solicitação', 'Outros').strip()
                    email_template = self.email_templates.get(motivo, self.email_templates['Outros'])
                    subject = "Requisição de Documentos"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.update_table()
                    self.back_to_main_view()

                def authorize_payment():
                    new_status = 'Pronto para pagamento'
                    timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                    self.sheets_handler.update_status(timestamp_str, new_status)

                    email_template = self.email_templates.get('Aprovação', 'Sua solicitação foi aprovada.')
                    subject = "Pagamento Autorizado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.update_table()
                    self.back_to_main_view()

                def cancel_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                        self.sheets_handler.update_status(timestamp_str, new_status)

                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.update_table()
                        self.back_to_main_view()

                button_width = 25
                request_button = tk.Button(
                    actions_tab,
                    text="Requerir Documentos",
                    command=request_documents,
                    bg="orange",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                request_button.pack(pady=10)

                authorize_button = tk.Button(
                    actions_tab,
                    text="Autorizar Pagamento",
                    command=authorize_payment,
                    bg="green",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                authorize_button.pack(pady=10)

                cancel_button = tk.Button(
                    actions_tab,
                    text="Recusar/Cancelar Auxílio",
                    command=cancel_auxilio,
                    bg="red",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                cancel_button.pack(pady=10)

            elif self.current_view == "Pronto para pagamento":
                def payment_made():
                    new_status = 'Pago'
                    timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                    self.sheets_handler.update_status(timestamp_str, new_status)

                    email_template = self.email_templates.get('Pagamento', 'Seu pagamento foi efetuado com sucesso.')
                    subject = "Pagamento Efetuado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.update_table()
                    self.back_to_main_view()

                def cancel_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora'].strftime('%d/%m/%Y %H:%M:%S')
                        self.sheets_handler.update_status(timestamp_str, new_status)

                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.update_table()
                        self.back_to_main_view()

                button_width = 25
                payment_button = tk.Button(
                    actions_tab,
                    text="Pagamento Efetuado",
                    command=payment_made,
                    bg="green",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                payment_button.pack(pady=10)

                cancel_button = tk.Button(
                    actions_tab,
                    text="Recusar/Cancelar Auxílio",
                    command=cancel_auxilio,
                    bg="red",
                    fg="white",
                    font=("Helvetica", 13),
                    width=button_width
                )
                cancel_button.pack(pady=10)

        # Aba "Histórico de solicitações"
        history_tab = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(history_tab, text="Histórico de solicitações")

        cpf = str(row_data.get('CPF:', '')).strip()
        all_data = self.sheets_handler.load_data()
        all_data['CPF:'] = all_data['CPF:'].astype(str).str.strip()
        history_data = all_data[all_data['CPF:'] == cpf]

        history_columns = ['Carimbo de data/hora', 'Ultima Atualizacao', 'Valor', 'Status']

        history_tree = ttk.Treeview(history_tab, columns=history_columns, show='headings', height=10)
        history_tree.pack(fill='both', expand=True)

        for col in history_columns:
            history_tree.heading(
                col,
                text=col,
                command=lambda _col=col: self.treeview_sort_column(history_tree, _col, False)
            )
            history_tree.column(col, anchor='center', width=100)

        self.history_tree_data = history_data.copy()

        for idx, hist_row in history_data.iterrows():
            values = [hist_row[col] for col in history_columns]
            history_tree.insert("", "end", iid=str(idx), values=values)

        history_tree.bind("<Double-1>", self.on_history_treeview_click)

        self.back_button.pack(side='bottom', pady=20)

    def on_history_treeview_click(self, event):
        """
        Ao dar duplo clique em um item do histórico de solicitações, abre
        uma nova janela com detalhes daquela solicitação.
        """
        selected_item = event.widget.selection()
        if selected_item:
            item_iid = selected_item[0]
            selected_row = self.history_tree_data.loc[int(item_iid)]
            self.show_details_in_new_window(selected_row)

    def show_details_in_new_window(self, row_data):
        """
        Abre uma nova janela Tkinter para exibir os detalhes de uma solicitação específica.
        """
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detalhes da Solicitação")
        detail_window.geometry("800x600")
        detail_window.configure(bg=self.bg_color)

        detail_frame = tk.Frame(detail_window, bg=self.bg_color)
        detail_frame.pack(fill="both", expand=True)

        details_title_label = tk.Label(
            detail_frame,
            text="Detalhes da Solicitação",
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color
        )
        details_title_label.pack(pady=10)

        notebook_style = ttk.Style()
        notebook_style.theme_use('default')
        notebook_style.configure("CustomNotebook.TNotebook", background=self.bg_color)
        notebook_style.configure("CustomNotebook.TNotebook.Tab", background=self.bg_color, font=("Helvetica", 13))
        notebook_style.configure('Custom.TFrame', background=self.bg_color)
        notebook_style.configure("CustomBold.TLabel", font=("Helvetica", 12, "bold"), background=self.bg_color)
        notebook_style.configure("CustomRegular.TLabel", font=("Helvetica", 12), background=self.bg_color)

        notebook = ttk.Notebook(detail_frame, style="CustomNotebook.TNotebook")
        notebook.pack(fill='both', expand=True)

        sections = {
            "Informações Pessoais": [
                'Nome completo (sem abreviações):',
                'Endereço de e-mail',
                'Telefone de contato:',
                'CPF:',
                'RG/RNE:',
                'Endereço completo (logradouro, número, bairro, cidade e estado)'
            ],
            "Informações Acadêmicas": [
                'Ano de ingresso o PPG:',
                'Curso:',
                'Orientador',
                'Possui bolsa?',
                'Qual a agência de fomento?',
                'Título do projeto do qual participa:',
            ],
            "Detalhes da Solicitação": [
                'Motivo da solicitação',
                'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
                'Local de realização do evento',
                'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias (para transporte, hospedagem e alimentação), passagem aérea, pagamento de análises e traduções, etc.\n',
            ],
            "Informações Financeiras": [
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        for section_name, fields in sections.items():
            tab_frame = ttk.Frame(notebook, style='Custom.TFrame')
            notebook.add(tab_frame, text=section_name)

            tab_frame.columnconfigure(0, weight=1, minsize=200)
            tab_frame.columnconfigure(1, weight=3)

            row_idx = 0
            for col in fields:
                if col in row_data:
                    label = ttk.Label(tab_frame, text=f"{col}:", style="CustomBold.TLabel", wraplength=200, justify='left')
                    label.grid(row=row_idx, column=0, sticky='nw', padx=10, pady=5)
                    value = ttk.Label(tab_frame, text=str(row_data[col]), style="CustomRegular.TLabel", wraplength=600, justify="left")
                    value.grid(row=row_idx, column=1, sticky='nw', padx=10, pady=5)
                    row_idx += 1

        close_button = tk.Button(detail_frame, text="Fechar", command=detail_window.destroy, bg=self.button_bg_color)
        close_button.pack(pady=10)

    def ask_send_email(self, row_data, new_status, new_value=None):
        """
        Abre uma janela perguntando se deseja enviar e-mail ao solicitante
        para notificar a mudança de status.
        """
        send_email = messagebox.askyesno("Enviar E-mail", "Deseja enviar um e-mail notificando a alteração de status?")
        if send_email:
            email_window = tk.Toplevel(self.root)
            email_window.title("Enviar E-mail")

            recipient_label = tk.Label(email_window, text="Destinatário:")
            recipient_label.pack(anchor="w", padx=10, pady=5)
            recipient_email = row_data['Endereço de e-mail']
            recipient_entry = tk.Entry(email_window, width=50)
            recipient_entry.insert(0, recipient_email)
            recipient_entry.pack(anchor="w", padx=10, pady=5)

            email_body_label = tk.Label(email_window, text="Corpo do E-mail:")
            email_body_label.pack(anchor="w", padx=10, pady=5)
            email_body_text = Text(email_window, width=60, height=15)

            email_body = (
                f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                f"Seu status foi alterado para: {new_status}."
            )
            if new_value:
                email_body += f"\nValor do auxílio: R$ {new_value}."
            email_body += (
                f"\nCurso: {row_data['Curso:']}.\nOrientador: {row_data['Orientador']}."
                f"\n\nAtt,\nEquipe de Suporte"
            )
            email_body_text.insert(tk.END, email_body)
            email_body_text.pack(anchor="w", padx=10, pady=5)

            def send_email_action():
                recipient = recipient_entry.get()
                subject = "Atualização de Status"
                body = email_body_text.get("1.0", tk.END)
                self.email_sender.send_email(recipient, subject, body)
                email_window.destroy()

            send_button = tk.Button(email_window, text="Enviar E-mail", command=send_email_action)
            send_button.pack(pady=10)

    def send_custom_email(self, recipient, subject, body):
        """
        Abre uma janela para editar e enviar um email customizado.
        """
        email_window = tk.Toplevel(self.root)
        email_window.title("Enviar E-mail")

        recipient_label = tk.Label(email_window, text="Destinatário:")
        recipient_label.pack(anchor="w", padx=10, pady=5)
        recipient_entry = tk.Entry(email_window, width=50)
        recipient_entry.insert(0, recipient)
        recipient_entry.pack(anchor="w", padx=10, pady=5)

        email_body_label = tk.Label(email_window, text="Corpo do E-mail:")
        email_body_label.pack(anchor="w", padx=10, pady=5)
        email_body_text = Text(email_window, width=60, height=15)
        email_body_text.insert(tk.END, body)
        email_body_text.pack(anchor="w", padx=10, pady=5)

        def send_email_action():
            recipient_addr = recipient_entry.get()
            email_body = email_body_text.get("1.0", tk.END)
            self.email_sender.send_email(recipient_addr, subject, email_body)
            email_window.destroy()

        send_button = tk.Button(email_window, text="Enviar E-mail", command=send_email_action)
        send_button.pack(pady=10)

    def show_statistics(self):
        """
        Exibe a tela de estatísticas sobre as solicitações.
        """
        if self.welcome_frame.winfo_ismapped():
            self.welcome_frame.pack_forget()
        if self.table_frame.winfo_ismapped():
            self.table_frame.pack_forget()
        if self.details_frame and self.details_frame.winfo_ismapped():
            self.details_frame.pack_forget()
            self.details_frame.destroy()
            self.details_frame = None

        if self.back_button.winfo_ismapped():
            self.back_button.pack_forget()

        self.update_selected_button("Estatísticas")

        self.statistics_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.statistics_frame.pack(fill='both', expand=True)
        self.display_statistics()

    def display_statistics(self):
        """
        Carrega dados, calcula estatísticas e exibe num frame + alguns gráficos.
        """
        for widget in self.statistics_frame.winfo_children():
            widget.destroy()

        self.data = self.sheets_handler.load_data()

        # Converter 'Valor' para numérico
        self.data['Valor'] = self.data['Valor'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)')[0]
        self.data['Valor'] = pd.to_numeric(self.data['Valor'], errors='coerce').fillna(0)

        total_requests = len(self.data)
        pending_requests = len(self.data[self.data['Status'].isin(['Autorizado', 'Aguardando documentação'])])
        awaiting_payment_requests = len(self.data[self.data['Status'] == 'Pronto para pagamento'])
        paid_requests = len(self.data[self.data['Status'] == 'Pago'])
        total_paid_values = self.data[self.data['Status'] == 'Pago']['Valor'].sum()
        total_released_values = self.data[self.data['Status'].isin(['Pago', 'Pronto para pagamento'])]['Valor'].sum()

        stats_text = (
            f"Número total de solicitações: {total_requests}\n"
            f"Número de solicitações pendentes: {pending_requests}\n"
            f"Número de solicitações aguardando pagamento: {awaiting_payment_requests}\n"
            f"Número de solicitações pagas: {paid_requests}\n"
            f"Soma dos valores já pagos: R$ {total_paid_values:.2f}\n"
            f"Soma dos valores já liberados: R$ {total_released_values:.2f}\n"
        )

        stats_label = tk.Label(
            self.statistics_frame,
            text=stats_text,
            font=("Helvetica", 12),
            bg=self.bg_color,
            justify='left'
        )
        stats_label.pack(pady=10, padx=10, anchor='w')

        # Criar gráficos
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        plt.subplots_adjust(hspace=0.5, wspace=0.3)

        # Gráfico de barras dos valores pagos ao longo do tempo
        paid_data = self.data[self.data['Status'] == 'Pago'].copy()
        if not paid_data.empty:
            paid_data['Ultima Atualizacao'] = pd.to_datetime(
                paid_data['Ultima Atualizacao'],
                format='%d/%m/%Y %H:%M:%S',
                errors='coerce'
            )
            paid_data = paid_data.dropna(subset=['Ultima Atualizacao'])
            paid_data_grouped = paid_data.groupby(paid_data['Ultima Atualizacao'].dt.date)['Valor'].sum()
            paid_data_grouped.plot(kind='bar', ax=axes[0, 0])
            axes[0, 0].set_title('Valores Pagos ao Longo do Tempo')
            axes[0, 0].set_xlabel('Data')
            axes[0, 0].set_ylabel('Valor Pago (R$)')
        else:
            axes[0, 0].text(
                0.5, 0.5,
                'Nenhum pagamento realizado ainda.',
                horizontalalignment='center',
                verticalalignment='center'
            )
            axes[0, 0].set_title('Valores Pagos ao Longo do Tempo')
            axes[0, 0].axis('off')

        # Gráfico de pizza por Motivo da Solicitação
        motivo_counts = self.data['Motivo da solicitação'].value_counts()
        motivo_counts.plot(kind='pie', ax=axes[0, 1], autopct='%1.1f%%')
        axes[0, 1].set_ylabel('')
        axes[0, 1].set_title('Distribuição por Motivo da Solicitação')

        # Gráfico de pizza por Agência de Fomento
        agencia_counts = self.data['Qual a agência de fomento?'].value_counts()
        agencia_counts.plot(kind='pie', ax=axes[1, 0], autopct='%1.1f%%')
        axes[1, 0].set_ylabel('')
        axes[1, 0].set_title('Distribuição por Agência de Fomento')

        # Gráfico de barras do número de solicitações por Status
        status_counts = self.data['Status'].value_counts()
        status_counts.plot(kind='bar', ax=axes[1, 1])
        axes[1, 1].set_title('Solicitações por Status')
        axes[1, 1].set_xlabel('Status')
        axes[1, 1].set_ylabel('Número de Solicitações')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.statistics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def open_settings(self):
        """
        Abre uma janela de configurações para editar os modelos de e-mail.
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("600x600")
        settings_window.configure(bg=self.bg_color)

        instructions = (
            "Nesta seção, você pode editar os modelos de e-mail utilizados.\n"
            "Use chaves para inserir dados do formulário. Por exemplo:\n"
            "{Nome} será substituído pelo nome do solicitante."
        )

        instructions_label = tk.Label(
            settings_window,
            text=instructions,
            bg=self.bg_color,
            font=("Helvetica", 12),
            justify='left'
        )
        instructions_label.pack(pady=10, padx=10)

        # Criar botões para editar cada modelo de e-mail
        for motivo in self.email_templates.keys():
            button = tk.Button(
                settings_window,
                text=f"Editar E-mail para {motivo}",
                command=lambda m=motivo: self.edit_email_template(m),
                bg=self.button_bg_color
            )
            button.pack(pady=5, padx=10, fill='x')

    def edit_email_template(self, motivo):
        """
        Abre uma janela para editar o template de e-mail referente ao 'motivo' selecionado.
        """
        template_window = tk.Toplevel(self.root)
        template_window.title(f"Editar Modelo de E-mail para {motivo}")
        template_window.geometry("600x400")
        template_window.configure(bg=self.bg_color)

        label = tk.Label(
            template_window,
            text=f"Editando o modelo de e-mail para {motivo}:",
            bg=self.bg_color,
            font=("Helvetica", 12)
        )
        label.pack(pady=10)

        text_widget = Text(template_window, width=70, height=15)
        text_widget.pack(pady=10, padx=10)
        text_widget.insert(tk.END, self.email_templates[motivo])

        def save_template():
            new_template = text_widget.get("1.0", tk.END).strip()
            self.email_templates[motivo] = new_template
            self.save_email_templates()
            template_window.destroy()

        save_button = tk.Button(template_window, text="Salvar", command=save_template, bg="green", fg="white")
        save_button.pack(pady=10)
