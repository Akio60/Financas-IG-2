# details_manager.py

import threading
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.constants import *
from tkinter import Text, messagebox, BOTH
from datetime import datetime
import json
import os
import uuid
import pandas as pd  # Adicionando import do pandas
import logger_app
from tkinter import filedialog

FORM_FIELD_MAPPING = {
    'Nome completo (sem abreviações):': 'Nome do Solicitante',
    'Endereço de e-mail': 'E-mail Pessoal',
    'Telefone de contato:': 'Telefone Principal',
    'CPF:': 'CPF do Aluno',
    'RG/RNE:': 'Documento de Identidade',
    'Endereço completo (logradouro, número, bairro, cidade e estado)': 'Endereço Residencial',
    'Ano de ingresso o PPG:': 'Ano de Ingresso no Programa',
    'Curso:': 'Curso Matriculado',
    'Orientador': 'Professor Orientador',
    'Possui bolsa?': 'Possui Bolsa',
    'Qual a agência de fomento?': 'Agência de Fomento',
    'Título do projeto do qual participa:': 'Título do Projeto',
    'Motivo da solicitação': 'Motivo do Pedido',
    'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A':
        'Nome do Evento/Atividade',
    'Local de realização do evento': 'Local do Evento',
    'Período de realização da atividade. Indique as datas (dd/mm/aaaa)': 'Período da Atividade',
    'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias ...':
        'Itens a Financiar',
    'Valor solicitado. Somente valor, sem pontos e vírgula' : 'Valor Solicitado (R$)',
    'Valor': 'Valor liberado para a solicitação',
    'Dados bancários (banco, agência e conta) ': 'Dados Bancários',
    'Descrever a solicitação resumidamente': 'Resumo da Solicitação',
    'Observações'   : 'Observações'
}

class DetailsManager:
    def __init__(self, app):
        self.app = app
        self.FORM_FIELD_MAPPING = FORM_FIELD_MAPPING
        self.edit_mode = False
        self.original_text = ""
        self.attachment_path = None  # Nova variável para armazenar caminho do anexo

    def show_details_in_place(self, row_data):
        if self.app.user_role == "A1":
            messagebox.showinfo("Aviso", "Cargo A1 não acessa detalhes.")
            return

        # Oculta o frame da tabela principal, se existir
        if self.app.table_frame and self.app.table_frame.winfo_exists():
            self.app.table_frame.pack_forget()

        self.app.details_frame = tb.Frame(self.app.content_frame)
        self.app.details_frame.pack(fill=BOTH, expand=True)

        self.app.details_title_label = tb.Label(
            self.app.details_frame, text="Controle de Orçamento IG - PPG UNICAMP",
            font=("Helvetica", 16, "bold")
        )
        self.app.details_title_label.pack(pady=10)

        notebook = tb.Notebook(self.app.details_frame, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True)

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
                'Id',
                'Motivo da solicitação',
                'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
                'Local de realização do evento',
                'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias ...',
                'Descrever a solicitação resumidamente',
                'Observações'
            ],
            "Informações Financeiras": [
                'Valor solicitado. Somente valor, sem pontos e vírgula',
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        for section_name, fields in sections.items():
            tab_frame = tb.Frame(notebook)
            notebook.add(tab_frame, text=section_name)

            # Configuração consistente do grid
            tab_frame.columnconfigure(0, weight=1, minsize=300)  # Coluna dos labels
            tab_frame.columnconfigure(1, weight=3, minsize=400)  # Coluna dos valores

            row_idx = 0
            for col in fields:
                if col in row_data:
                    if col == 'Observações':
                        # Label de título acima do frame
                        display_label = self.FORM_FIELD_MAPPING.get(col, col)
                        title_label = tb.Label(tab_frame, text=f"{display_label}:", font=("Helvetica", 12, "bold"))
                        title_label.grid(row=row_idx, column=0, columnspan=2, sticky='w', padx=20, pady=(10,0))  # Aumenta o pady superior
                        row_idx += 1

                        # Frame para conter a caixa de texto e botões
                        obs_frame = tb.Frame(tab_frame)
                        obs_frame.grid(row=row_idx, column=0, columnspan=2, sticky='nsew', padx=20, pady=(30,50))  # Aumenta o pady superior
                        
                        # Configurar grid do obs_frame
                        obs_frame.columnconfigure(0, weight=5)  # Coluna da caixa de texto
                        obs_frame.columnconfigure(1, weight=1)  # Coluna dos botões
                        
                        # Caixa de texto para observações com o texto atual
                        self.obs_text = Text(obs_frame, height=4, state='normal')
                        self.obs_text.grid(row=0, column=0, sticky='nsew')
                        
                        # Inserir o texto das observações da planilha
                        observation_text = row_data.get('Observações', '')
                        if observation_text is None:
                            observation_text = ''
                        self.obs_text.delete('1.0', 'end')
                        self.obs_text.insert('1.0', str(observation_text))
                        self.obs_text.config(state='disabled')
                        
                        # Frame para botões
                        btn_frame = tb.Frame(obs_frame)
                        btn_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
                        
                        # Configurar grid do btn_frame para distribuir os botões igualmente
                        btn_frame.rowconfigure(0, weight=1)
                        btn_frame.rowconfigure(1, weight=1)
                        btn_frame.rowconfigure(2, weight=1)
                        btn_frame.columnconfigure(0, weight=1)
                        
                        # Botão de editar
                        self.edit_btn = tb.Button(
                            btn_frame, 
                            text="Editar", 
                            bootstyle=PRIMARY,
                            command=lambda: self.toggle_edit_mode(row_data)
                        )
                        self.edit_btn.grid(row=0, column=0, sticky='nsew', pady=2)
                        
                        # Botões de confirmar e cancelar (inicialmente desabilitados)
                        self.confirm_btn = tb.Button(
                            btn_frame,
                            text="Confirmar",
                            bootstyle=SUCCESS,
                            command=lambda: self.save_observations(row_data),
                            state='disabled'
                        )
                        self.confirm_btn.grid(row=1, column=0, sticky='nsew', pady=2)
                        
                        self.cancel_btn = tb.Button(
                            btn_frame,
                            text="Cancelar",
                            bootstyle=DANGER,
                            command=self.cancel_edit,
                            state='disabled'
                        )
                        self.cancel_btn.grid(row=2, column=0, sticky='nsew', pady=2)
                        
                        # Incrementa row_idx para o próximo item
                        row_idx += 1
                        continue
                    else:
                        display_label = self.FORM_FIELD_MAPPING.get(col, col)
                        
                        # Frame para conter cada par label-valor
                        field_frame = tb.Frame(tab_frame)
                        field_frame.grid(row=row_idx, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
                        
                        # Configuração do grid do field_frame
                        field_frame.columnconfigure(0, minsize=300, weight=0)  # Largura fixa para labels
                        field_frame.columnconfigure(1, weight=1)   # Valor expande
                        
                        # Label com wrapping
                        label = tb.Label(
                            field_frame, 
                            text=f"{display_label}:", 
                            font=("Helvetica", 12, "bold"),
                            wraplength=280,  # Permite quebra de texto
                            justify="left"    # Alinha o texto quebrado à esquerda
                        )
                        label.grid(row=0, column=0, sticky='nw', padx=(0,20))
                        
                        # Valor com wrapping
                        value_text = str(row_data[col])
                        value = tb.Label(
                            field_frame, 
                            text=value_text, 
                            font=("Helvetica", 12),
                            wraplength=400,  # Permite quebra de texto
                            justify="left",   # Alinha o texto quebrado à esquerda
                        )
                        value.grid(row=0, column=1, sticky='nw')
                        
                        # Configura o grid para expandir na vertical se necessário
                        field_frame.grid_rowconfigure(0, weight=1)
                        
                    row_idx += 1

            if section_name == "Informações Financeiras":
                if row_data['Status'] == '':
                    if self.app.user_role in ["A3", "A5"]:
                        value_label = tb.Label(tab_frame, text="Valor (R$):", font=("Helvetica", 12, "bold"))
                        value_label.grid(row=row_idx, column=0, sticky='w', padx=20, pady=5)
                        value_entry = tb.Entry(tab_frame, width=50)
                        value_entry.grid(row=row_idx, column=0, sticky='w', padx=320, pady=5)
                        self.app.value_entry = value_entry
                        row_idx += 1

                        def autorizar_auxilio():
                            value_entry = self.app.value_entry
                            new_value = value_entry.get().strip()
                            if not new_value:
                                messagebox.showwarning("Aviso", "Insira um valor antes.")
                                return
                            new_status = 'Solicitação Aceita'
                            ts_str = row_data['Carimbo de data/hora']
                            
                            # Removida atualização direta do status e valor
                            notification_data = self.prepare_notification_data(new_status, row_data)
                            self.unified_email_window(row_data, new_status, notification_data, new_value)

                        def negar_auxilio():
                            confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                            if confirm:
                                new_status = 'Cancelado'
                                # Removida atualização direta do status
                                notification_data = self.prepare_notification_data("Cancelado", row_data)
                                self.unified_email_window(row_data, new_status, notification_data)

                        autorizar_button = tb.Button(tab_frame, text="Autorizar Auxílio", bootstyle=SUCCESS, command=autorizar_auxilio)
                        negar_button = tb.Button(tab_frame, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=negar_auxilio)
                        autorizar_button.grid(row=row_idx, column=0, padx=320, pady=10, sticky='w')
                        negar_button.grid(row=row_idx, column=0, padx=480, pady=10, sticky='w')
                        row_idx += 1

                # Histórico de Solicitações – ajuste de espaçamento
                history_label = tb.Label(tab_frame, text="Histórico de Solicitações", font=("Helvetica", 12, "bold"))
                history_label.grid(row=row_idx, column=0, columnspan=2, sticky='w', padx=20, pady=(10,5))
                row_idx += 1
                history_frame = tb.Frame(tab_frame, padding=(20,10))
                history_frame.grid(row=row_idx, column=0, columnspan=2, sticky='nsew', padx=20, pady=(5,20))
                tab_frame.rowconfigure(row_idx, weight=1)

                history_columns = [
                    'Id',
                    'Carimbo de data/hora',
                    'Ultima Atualizacao',
                    'Valor',
                    'Status'
                ]
                history_tree = tb.Treeview(history_frame, columns=history_columns, show='headings', height=10)
                history_tree.pack(fill=BOTH, expand=True)

                for col in history_columns:
                    history_tree.heading(
                        col, text=col,
                        command=lambda _col=col: self.app.treeview_sort_column(history_tree, _col, False)
                    )
                    history_tree.column(col, anchor='center', width=120)

                all_data = self.app.sheets_handler.load_data()
                cpf = str(row_data.get('CPF:', '')).strip()
                all_data['CPF:'] = all_data['CPF:'].astype(str).str.strip()
                history_data = all_data[all_data['CPF:'] == cpf]
                # Armazena os dados históricos para uso no clique duplo
                self.app.history_tree_data = history_data.copy()

                for idx, hist_row in history_data.iterrows():
                    values = [hist_row.get(c, "") for c in history_columns]
                    history_tree.insert("", "end", iid=str(idx), values=values)
                history_tree.bind("<Double-1>", self.on_history_treeview_click)
                row_idx += 1

        if self.app.user_role in ["A3", "A4", "A5"] and self.app.current_view != "Aguardando aprovação":
            self.add_actions_tab(notebook, row_data)

        back_button = tb.Button(self.app.details_frame, text="Voltar", bootstyle=PRIMARY, command=self.app.go_to_home)
        back_button.pack(side='bottom', pady=20)

    def on_history_treeview_click(self, event):
        selected_item = event.widget.selection()
        if (selected_item):
            item_iid = selected_item[0]
            selected_row = self.app.history_tree_data.loc[int(item_iid)]
            self.show_details_in_new_window(selected_row)

    def notify_next_responsible(self, event_key, row_data):
        """Agora chama diretamente o unified_email_window"""
        notification_data = self.prepare_notification_data(event_key, row_data)
        if notification_data:
            self.unified_email_window(row_data, event_key, notification_data)

    def add_actions_tab(self, notebook, row_data):
        view = self.app.current_view
        role = self.app.user_role
        actions_tab = tb.Frame(notebook)
        notebook.add(actions_tab, text="Ações")
        
        # Configura o grid com 7 colunas e centralização
        for i in range(7):
            actions_tab.columnconfigure(i, weight=1)
        actions_tab.rowconfigure(0, weight=1)  # Espaço superior
        actions_tab.rowconfigure(4, weight=1)  # Espaço inferior
        
        # Define um tamanho padrão para todos os botões
        BTN_WIDTH = 250
        BTN_PAD = 10

        # Funções de callback permanecem as mesmas
        def authorize_payment():
            if role not in ["A3", "A5"]:
                messagebox.showwarning("Permissão Negada", "Somente A3 ou A5.")
                return
            new_status = 'Pronto para pagamento'
            ts_str = row_data['Carimbo de data/hora']
            
            # Removida atualização direta do status
            notification_data = self.prepare_notification_data("ProntoPagamento", row_data)
            self.unified_email_window(row_data, new_status, notification_data)

        def cancel_auxilio():
            if role not in ["A3", "A5"]:
                messagebox.showwarning("Negado", "Somente A3 ou A5 podem cancelar.")
                return
                
            confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja recusar/cancelar o auxílio?")
            if confirm:
                new_status = 'Cancelado'
                # Removida atualização direta do status
                notification_data = self.prepare_notification_data("Cancelado", row_data)
                self.unified_email_window(row_data, new_status, notification_data)

        def payment_made():
            if role not in ["A3", "A4", "A5"]:
                messagebox.showwarning("Negado", "Você não tem permissão para efetuar pagamento.")
                return
            new_status = 'Pago'
            # Removida atualização direta do status
            notification_data = self.prepare_notification_data("Pago", row_data)
            self.unified_email_window(row_data, new_status, notification_data)

        # Layout centralizado por view
        if view == "Aceitas":
            # Coloca os botões com largura menor nas colunas 2, 3 e 4 (centro do grid 7x5)
            req_btn = tb.Button(
            actions_tab, 
            text="Requerir Documentos",
            width=50,
            bootstyle=WARNING,
            command=lambda: self.request_documents(row_data)
            )
            req_btn.grid(row=1, column=2, columnspan=3, pady=BTN_PAD)

            auth_btn = tb.Button(
            actions_tab,
            text="Autorizar Pagamento", 
            width=50,
            bootstyle=SUCCESS,
            command=authorize_payment
            )
            auth_btn.grid(row=2, column=2, columnspan=3, pady=BTN_PAD)

            cancel_btn = tb.Button(
            actions_tab,
            text="Recusar/Cancelar Auxílio",
            width=50,
            bootstyle=DANGER,
            command=cancel_auxilio
            )
            cancel_btn.grid(row=3, column=2, columnspan=3, pady=BTN_PAD)

        elif view == "Aguardando documentos":
            auth_btn = tb.Button(
            actions_tab,
            text="Autorizar Pagamento",
            width=50,
            bootstyle=SUCCESS,
            command=authorize_payment
            )
            auth_btn.grid(row=1, column=2, columnspan=3, pady=BTN_PAD)

            cancel_btn = tb.Button(
            actions_tab,
            text="Recusar/Cancelar Auxílio",
            width=50,
            bootstyle=DANGER,
            command=cancel_auxilio
            )
            cancel_btn.grid(row=2, column=2, columnspan=3, pady=BTN_PAD)

            req_btn = tb.Button(
            actions_tab,
            text="Requerir Documentos Novamente",
            width=50,
            bootstyle=WARNING,
            command=lambda: self.request_documents(row_data)
            )
            req_btn.grid(row=3, column=2, columnspan=3, pady=BTN_PAD)

        elif view == "Pronto para pagamento":
            payment_btn = tb.Button(
            actions_tab,
            text="Pagamento Efetuado",
            width=50,
            bootstyle=SUCCESS,
            command=payment_made
            )
            payment_btn.grid(row=1, column=2, columnspan=3, pady=BTN_PAD)

            cancel_btn = tb.Button(
            actions_tab,
            text="Recusar/Cancelar Auxílio",
            width=50,
            bootstyle=DANGER,
            command=cancel_auxilio
            )
            cancel_btn.grid(row=2, column=2, columnspan=3, pady=BTN_PAD)

    def _center_window(self, window, w, h):
        """Centraliza qualquer janela"""
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        window.geometry(f"{w}x{h}+{x}+{y}")

    def show_details_in_new_window(self, row_data):
        detail_window = tb.Toplevel(self.app.root)
        detail_window.title("Detalhes da Solicitação")
        w, h = 800, 600  # Tamanho fixo
        self._center_window(detail_window, w, h)
        # Impedir redimensionamento e maximização
        detail_window.resizable(False, False)
        # Remover botões de maximizar/minimizar
        detail_window.attributes('-toolwindow', True)

        detail_frame = tb.Frame(detail_window)
        detail_frame.pack(fill=BOTH, expand=True)

        details_title_label = tb.Label(detail_frame, text="Detalhes da Solicitação", font=("Helvetica", 16, "bold"))
        details_title_label.pack(pady=10)

        notebook = tb.Notebook(detail_frame, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True)

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
                'Id',
                'Motivo da solicitação',
                'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
                'Local de realização do evento',
                'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Descrever detalhadamente os itens a serem financiados...',
                'Valor solicitado. Somente valor, sem pontos e vírgula',
                'Descrever a solicitação resumidamente',
                'Observações'
            ],
            "Informações Financeiras": [
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        row_idx = 0
        for section_name, fields in sections.items():
            tab_frame = tb.Frame(notebook)
            notebook.add(tab_frame, text=section_name)

            tab_frame.columnconfigure(0, weight=1, minsize=200)
            tab_frame.columnconfigure(1, weight=3)

            row_idx = 0
            for col in fields:
                if col in row_data:
                    display_label = self.FORM_FIELD_MAPPING.get(col, col)
                    
                    # Ajuste para janela de detalhes pop-up
                    label = tb.Label(
                        tab_frame, 
                        text=f"{display_label}:", 
                        font=("Helvetica", 12, "bold"),
                        wraplength=250,
                        justify="left"
                    )
                    label.grid(row=row_idx, column=0, sticky='nw', padx=10, pady=5)

                    value_text = str(row_data[col])
                    value = tb.Label(
                        tab_frame, 
                        text=value_text, 
                        font=("Helvetica", 12),
                        wraplength=350,
                        justify="left"
                    )
                    value.grid(row=row_idx, column=1, sticky='nw', padx=10, pady=5)
                    
                    # Configura o grid para expandir na vertical
                    tab_frame.grid_rowconfigure(row_idx, weight=1)
                    
                    row_idx += 1

        close_button = tb.Button(detail_frame, text="Fechar", bootstyle=PRIMARY, command=detail_window.destroy)
        close_button.pack(pady=10)

    def send_emails_and_update_status(self, emails_to_send, row_data, new_status=None, new_value=None):
        """Função unificada para enviar emails e atualizar status com interface padronizada"""
        
        progress_window = tb.Toplevel(self.app.root)
        progress_window.title("Enviando Emails")
        w, h = 500, 400
        self._center_window(progress_window, w, h)
        progress_window.resizable(False, False)
        progress_window.attributes('-toolwindow', True)
        progress_window.attributes('-topmost', True)  # Mantém janela sempre visível
        progress_window.transient(self.app.root)
        progress_window.grab_set()
        progress_window.focus_set()

        main_frame = tb.Frame(progress_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Frame com título e lista de emails
        list_frame = tb.LabelFrame(main_frame, text="Emails a serem enviados", padding=10)
        list_frame.pack(fill=BOTH, expand=True)

        # Treeview para mostrar status dos envios
        columns = ("Destinatário", "Tipo", "Status")
        tree = tb.Treeview(list_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Scrollbar para a Treeview
        scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Adiciona emails na lista
        for i, email in enumerate(emails_to_send):
            tree.insert("", END, iid=str(i), values=(
                email["recipient"],
                email["type"],
                "Pendente"
            ))

        # Barra de progresso estilizada
        progress = tb.Progressbar(
            main_frame, 
            bootstyle="success-striped",
            maximum=len(emails_to_send)
        )
        progress.pack(fill=X, pady=10)

        status_label = tb.Label(main_frame, text="Iniciando envio...")
        status_label.pack(pady=5)

        def process_emails():
            try:
                all_success = True
                success_count = 0

                for i, email in enumerate(emails_to_send):
                    try:
                        if not progress_window.winfo_exists():
                            return
                            
                        status_label.config(text=f"Enviando para {email['recipient']}...")
                        self.app.email_sender.send_email(
                            email["recipient"],
                            email["subject"],
                            email["body"],
                            email.get("attachment")
                        )
                        tree.set(str(i), "Status", "✓ Enviado")
                        success_count += 1
                        
                        # Log de sucesso
                        logger_app.append_log(
                            logger_app.LogLevel.INFO,
                            logger_app.LogCategory.EMAIL,
                            "SYSTEM",
                            "SEND_EMAIL",
                            f"Email enviado com sucesso para {email['recipient']}"
                        )
                    except Exception as e:
                        tree.set(str(i), "Status", "✗ Erro")
                        all_success = False
                        # Log de erro
                        logger_app.append_log(
                            logger_app.LogLevel.ERROR,
                            logger_app.LogCategory.EMAIL,
                            "SYSTEM",
                            "SEND_EMAIL_ERROR",
                            f"Erro ao enviar email para {email['recipient']}: {str(e)}"
                        )

                    progress["value"] = i + 1
                    progress_window.update()

                if not progress_window.winfo_exists():
                    return
                    
                if all_success and new_status:
                    ts_str = row_data['Carimbo de data/hora']
                    if new_value:
                        self.app.sheets_handler.update_value(ts_str, new_value, self.app.user_name)
                    self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name)
                    status_label.config(
                        text=f"Concluído! {success_count} emails enviados. Status atualizado."
                    )
                else:
                    status_label.config(
                        text=f"Atenção! {success_count} de {len(emails_to_send)} emails enviados."
                    )

                close_btn.config(state="normal")
                
                if all_success:
                    progress_window.after(2000, lambda: [
                        progress_window.destroy() if progress_window.winfo_exists() else None,
                        self.app.update_table(),
                        self.app.go_to_home()
                    ])

            except tk.TclError:
                pass

        close_btn = tb.Button(
            main_frame,
            text="Fechar",
            command=progress_window.destroy,
            state="disabled"
        )
        close_btn.pack(pady=10)

        thread = threading.Thread(target=process_emails)
        thread.daemon = True
        thread.start()

    def unified_email_window(self, row_data, status_update, notification_data=None, value=None):
        """Janela unificada com abas para preview dos emails"""
        email_window = tb.Toplevel(self.app.root)
        email_window.title("Gerenciamento de Emails")
        w, h = 800, 600  # Tamanho fixo
        self._center_window(email_window, w, h)
        # Impedir redimensionamento e maximização
        email_window.resizable(False, False)
        # Remover botões de maximizar/minimizar
        email_window.attributes('-toolwindow', True)
        # Manter janela sempre no topo
        email_window.attributes('-topmost', True)

        # Frame principal com notebook
        notebook = tb.Notebook(email_window)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Tab para email ao solicitante
        solicitante_tab = tb.Frame(notebook)
        notebook.add(solicitante_tab, text="Email ao Solicitante")

        # Tab para emails de notificação (se houver)
        notificacao_tab = None
        if notification_data and notification_data.get('recipients'):
            notificacao_tab = tb.Frame(notebook)
            notebook.add(notificacao_tab, text="Emails de Notificação")

        # Configuração da aba do solicitante
        recipient_frame = tb.LabelFrame(solicitante_tab, text="Destinatário", padding=10)
        recipient_frame.pack(fill=X, padx=10, pady=5)
        
        recipient_email = row_data['Endereço de e-mail']
        recipient_entry = tb.Entry(recipient_frame, width=50)
        recipient_entry.insert(0, recipient_email)
        recipient_entry.pack(fill=X)

        email_frame = tb.LabelFrame(solicitante_tab, text="Mensagem", padding=10)
        email_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Template do email ao solicitante usando o mesmo mapeamento
        status_template_map = {
            '': 'AguardandoAprovacao',
            'Solicitação Aceita': 'Aprovação',
            'Pago': 'Pagamento', 
            'Cancelado': 'Cancelamento',
            'Pronto para pagamento': 'ProntoPagamento',
            'Aguardando documentação': 'AguardandoDocumentacao'
        }

        # Seleciona template baseado no motivo ou no status
        motivo = row_data.get('Motivo da solicitação', '')
        if status_update in ['', 'Aguardando documentação']:
            template = self.app.email_templates.get(motivo, self.app.email_templates['Outros'])
        else:
            template_key = status_template_map.get(status_update, 'Outros')
            template = self.app.email_templates.get(template_key, '')

        try:
            body = template.format(
                Nome=row_data.get('Nome completo (sem abreviações):', ''),
                Curso=row_data.get('Curso:', ''),
                Orientador=row_data.get('Orientador', ''),
                Valor=value or row_data.get('Valor', '0,00'),
                Motivo=row_data.get('Motivo da solicitação', ''),
                Data=datetime.now().strftime('%d/%m/%Y')
            )
        except KeyError as e:
            logger_app.log_error(f"Erro ao formatar template: {str(e)}")
            body = f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
            body += f"Seu status foi alterado para: {status_update}."
            if value:
                body += f"\nValor do auxílio: R$ {value}."
            body += f"\nCurso: {row_data['Curso:']}\nOrientador: {row_data['Orientador']}"
            body += "\n\nAtenciosamente,\nEquipe Financeira"

        solicitante_text = tb.ScrolledText(email_frame, width=70, height=15)
        solicitante_text.pack(fill=BOTH, expand=True)
        solicitante_text.insert('1.0', body)

        # Adiciona frame para anexo após o campo de texto do email
        attach_frame = tb.Frame(solicitante_tab)
        attach_frame.pack(fill=X, padx=10, pady=5)

        self.attachment_path = None  # Reset do caminho do anexo
        self.attachment_label = tb.Label(attach_frame, text="Nenhum arquivo anexado")
        self.attachment_label.pack(side=LEFT, padx=5)

        def select_attachment():
            # Temporariamente desabilita topmost para permitir diálogo de arquivo
            email_window.attributes('-topmost', False)
            file_path = filedialog.askopenfilename(
                title="Selecione um arquivo para anexar",
                filetypes=[
                    ("Documentos", "*.pdf;*.doc;*.docx"),
                    ("Imagens", "*.png;*.jpg;*.jpeg"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            # Reabilita topmost após seleção
            email_window.attributes('-topmost', True)
            email_window.lift()  # Traz a janela de volta para frente

            if file_path:
                self.attachment_path = file_path
                base_name = os.path.basename(file_path)
                if len(base_name) > 40:  # Limita o tamanho do nome mostrado
                    base_name = base_name[:37] + "..."
                self.attachment_label.config(text=f"Anexo: {base_name}")

        def clear_attachment():
            self.attachment_path = None
            self.attachment_label.config(text="Nenhum arquivo anexado")

        attach_btn = tb.Button(
            attach_frame,
            text="Anexar Arquivo",
            bootstyle=INFO,
            command=select_attachment
        )
        attach_btn.pack(side=LEFT, padx=5)

        clear_btn = tb.Button(
            attach_frame,
            text="Limpar Anexo",
            bootstyle=SECONDARY,
            command=clear_attachment
        )
        clear_btn.pack(side=LEFT, padx=5)

        # Se houver dados de notificação, configura a segunda aba
        if notification_data and notification_data.get('recipients'):
            notif_frame = tb.LabelFrame(notificacao_tab, text="Destinatários", padding=10)
            notif_frame.pack(fill=X, padx=10, pady=5)
            
            for email in notification_data['recipients']:
                tb.Label(notif_frame, text=email).pack(anchor=W)

            notif_msg_frame = tb.LabelFrame(notificacao_tab, text="Mensagem", padding=10)
            notif_msg_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

            notif_text = tb.ScrolledText(notif_msg_frame, width=70, height=15)
            notif_text.pack(fill=BOTH, expand=True)
            notif_text.insert('1.0', notification_data['body'])
            notif_text.config(state='disabled')  # Torna o texto das notificações não editável

        def send_emails():
            # Prepara lista de emails para enviar
            emails_to_send = []
            
            # Email para solicitante (agora com anexo)
            emails_to_send.append({
                "recipient": recipient_entry.get().strip(),
                "subject": f"Atualização de Status - {status_update}",
                "body": solicitante_text.get('1.0', 'end-1c'),
                "type": "Solicitante",
                "attachment": self.attachment_path  # Adiciona o caminho do anexo
            })
            
            # Emails de notificação
            if notification_data and notification_data.get('recipients'):
                for email in notification_data['recipients']:
                    emails_to_send.append({
                        "recipient": email.strip(),
                        "subject": notification_data['subject'],
                        "body": notification_data['body'],
                        "type": "Notificação"
                    })

            email_window.destroy()
            self.send_emails_and_update_status(emails_to_send, row_data, status_update, value)

        # Botões de ação
        btn_frame = tb.Frame(email_window)
        btn_frame.pack(fill=X, padx=10, pady=10)

        send_btn = tb.Button(
            btn_frame, 
            text="Enviar Todos os Emails", 
            bootstyle=SUCCESS,
            command=send_emails
        )
        send_btn.pack(side=LEFT, padx=5)

        cancel_btn = tb.Button(
            btn_frame, 
            text="Cancelar", 
            bootstyle=DANGER,
            command=email_window.destroy
        )
        cancel_btn.pack(side=LEFT, padx=5)

        return email_window

    def prepare_notification_data(self, event_key, row_data):
        """Helper para preparar dados de notificação"""
        notification_emails = self.app.sheets_handler.get_notification_emails()
        recipients = notification_emails.get(event_key, [])
        
        if recipients:
            # Lógica melhorada para determinar o valor aprovado
            try:
                # Tenta obter o valor da entry se existir e for acessível
                if (hasattr(self.app, 'value_entry') and 
                    self.app.value_entry and 
                    self.app.value_entry.winfo_exists()):
                    valor_aprovado = self.app.value_entry.get().strip()
                else:
                    # Caso contrário, usa o valor já registrado
                    valor_aprovado = row_data.get('Valor', '0,00')
            except Exception:
                # Em caso de qualquer erro, usa o valor já registrado
                valor_aprovado = row_data.get('Valor', '0,00')

            body = (
                f"Prezado(a) responsável,\n\n"
                f"Uma solicitação teve seu status alterado e requer sua atenção.\n\n"
                f"=== DETALHES DA SOLICITAÇÃO ===\n"
                f"Status: {event_key}\n"
                f"ID: {row_data.get('Id', 'N/A')}\n"
                f"Data: {row_data.get('Carimbo de data/hora', 'N/A')}\n\n"
                f"=== DADOS DO SOLICITANTE ===\n"
                f"Nome: {row_data.get('Nome completo (sem abreviações):', 'N/A')}\n"
                f"CPF: {row_data.get('CPF:', 'N/A')}\n"
                f"Curso: {row_data.get('Curso:', 'N/A')}\n"
                f"Orientador: {row_data.get('Orientador', 'N/A')}\n\n"
                f"=== INFORMAÇÕES FINANCEIRAS ===\n"
                f"Valor Solicitado: R$ {row_data.get('Valor solicitado. Somente valor, sem pontos e vírgula', '0,00')}\n"
                f"Valor Aprovado: R$ {valor_aprovado}\n"
                f"Motivo: {row_data.get('Motivo da solicitação', 'N/A')}\n\n"                
                f"Para acessar mais detalhes ou tomar ações, por favor acesse o sistema.\n\n"
                f"Atenciosamente,\n"
                f"Sistema Financeiro IG-UNICAMP\n\n"
                f"--\n"
                f"Este é um email automático. Para questões específicas, entre em contato com a\n"
                f"Gestão Financeira do IG através do email gestao.financeira@ig.unicamp.br"
            )

            return {
                'recipients': recipients,
                'subject': f"[Sistema Financeiro IG] Nova Solicitação - {event_key}",
                'body': body
            }
        return None

    def toggle_edit_mode(self, row_data):
        if not self.edit_mode:
            self.edit_mode = True
            self.cancel_btn.config(state='normal')
            self.confirm_btn.config(state='normal')
            self.edit_btn.config(state='disabled')
            self.obs_text.config(state='normal')
            self.original_text = self.obs_text.get('1.0', 'end-1c')  # Entrando no modo de edição

    def save_observations(self, row_data):
        ts_str = row_data['Carimbo de data/hora']
        new_text = self.obs_text.get('1.0', 'end-1c')
        self.app.sheets_handler.update_observations(ts_str, new_text)  # Atualizar no Google Sheets
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', self.original_text)  # Restaurar texto original
        self.obs_text.config(state='disabled')  # Desabilitar edição
        self.edit_mode = False
        self.cancel_btn.config(state='disabled')
        self.confirm_btn.config(state='disabled')
        self.edit_btn.config(state='normal')
        messagebox.showinfo("Sucesso", "Observações atualizadas com sucesso!")

    def cancel_edit(self):
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', self.original_text)  # Restaurar texto original
        self.obs_text.config(state='disabled')  # Desabilitar edição
        self.edit_mode = False
        self.cancel_btn.config(state='disabled')
        self.confirm_btn.config(state='disabled')
        self.edit_btn.config(state='normal')
        
    def send_direct_email(self, recipient, subject, body):
        """Envia email direto sem interface"""
        try:
            self.app.email_sender.send_email(recipient, subject, body)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar email: {str(e)}")
            return False

    def request_documents(self, row_data):
        if self.app.user_role not in ["A3", "A5"]:
            messagebox.showwarning("Permissão Negada", "Apenas A3 ou A5.")
            return
            
        new_status = 'Aguardando documentação'
        # Removida atualização direta do status
        notification_data = self.prepare_notification_data("AguardandoDocumentacao", row_data)
        self.unified_email_window(row_data, new_status, notification_data)
            
        self.app.update_table()
        self.app.go_to_home()
