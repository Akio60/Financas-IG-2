# details_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Text, messagebox, BOTH
from datetime import datetime
import json
import os
import uuid
import pandas as pd  # Adicionando import do pandas
import logger_app

NOTIFICATION_CARGOS_FILE = "notification_cargos.json"
USERS_DB_FILE = "users_db.json"

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

def load_notification_cargos():
    if os.path.exists(NOTIFICATION_CARGOS_FILE):
        with open(NOTIFICATION_CARGOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_users_db():
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

class DetailsManager:
    def __init__(self, app):
        self.app = app
        self.FORM_FIELD_MAPPING = FORM_FIELD_MAPPING
        self.edit_mode = False
        self.original_text = ""

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
                        value_label.grid(row=row_idx, column=0, sticky='w', padx=10, pady=5)
                        value_entry = tb.Entry(tab_frame, width=50)
                        value_entry.grid(row=row_idx, column=1, sticky='w', padx=10, pady=5)
                        self.app.value_entry = value_entry
                        row_idx += 1

                        def autorizar_auxilio():
                            new_value = value_entry.get().strip()
                            if not new_value:
                                messagebox.showwarning("Aviso", "Insira um valor antes.")
                                return
                            new_status = 'Autorizado'
                            ts_str = row_data['Carimbo de data/hora']
                            
                            # Primeiro atualiza o status e valor
                            if not self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                                messagebox.showerror("Erro", "Falha ao atualizar status")
                                return
                            if not self.app.sheets_handler.update_value(ts_str, new_value, self.app.user_name):
                                messagebox.showerror("Erro", "Falha ao atualizar valor")
                                return
                            
                            # Pergunta sobre os emails
                            self.ask_send_email(row_data, new_status, new_value)  # Email para o cliente
                            self.ask_send_notification_emails(new_status, row_data)  # Email para os notificados
                            
                            # Atualiza a interface
                            self.app.update_table()
                            self.app.go_to_home()

                        def negar_auxilio():
                            confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                            if confirm:
                                new_status = 'Cancelado'
                                ts_str = row_data['Carimbo de data/hora']
                                self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name)
                                self.notify_next_responsible("Cancelado", row_data)
                                self.ask_send_email(row_data, new_status)
                                self.app.update_table()
                                self.app.go_to_home()

                        autorizar_button = tb.Button(tab_frame, text="Autorizar Auxílio", bootstyle=SUCCESS, command=autorizar_auxilio)
                        negar_button = tb.Button(tab_frame, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=negar_auxilio)
                        autorizar_button.grid(row=row_idx, column=0, padx=10, pady=10, sticky='w')
                        negar_button.grid(row=row_idx, column=1, padx=10, pady=10, sticky='w')
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
        if selected_item:
            item_iid = selected_item[0]
            selected_row = self.app.history_tree_data.loc[int(item_iid)]
            self.show_details_in_new_window(selected_row)

    def notify_next_responsible(self, event_key, row_data):
        """Função que agora apenas chama o método de confirmação"""
        self.ask_send_notification_emails(event_key, row_data)

    def ask_send_notification_emails(self, event_key, row_data):
        """Pergunta se deseja enviar emails de notificação e mostra preview"""
        try:
            notification_emails = self.app.sheets_handler.get_notification_emails()
            recipients = notification_emails.get(event_key, [])
            
            if not recipients:
                logger_app.log_warning(f"Nenhum email configurado para notificação do evento: {event_key}")
                return

            confirm = messagebox.askyesno(
                "Enviar Notificações",
                f"Deseja enviar emails de notificação para os responsáveis? ({len(recipients)} destinatário(s))"
            )
            
            if not confirm:
                return

            # Janela de preview do email
            preview_window = tb.Toplevel(self.app.root)
            preview_window.title("Preview - Email de Notificação")
            preview_window.geometry("600x500")

            # Lista de destinatários
            recipient_frame = tb.LabelFrame(preview_window, text="Destinatários", padding=10)
            recipient_frame.pack(fill="x", padx=10, pady=5)
            
            for email in recipients:
                tb.Label(recipient_frame, text=email.strip()).pack(anchor="w")

            # Preview do email
            body_frame = tb.LabelFrame(preview_window, text="Corpo do Email", padding=10)
            body_frame.pack(fill="both", expand=True, padx=10, pady=5)

            body_text = tb.ScrolledText(body_frame, width=60, height=15)
            body_text.pack(fill="both", expand=True)

            subject = f"[Sistema Financeiro] Nova solicitação - Status: {event_key}"
            body = (
                f"Prezado(s),\n\n"
                f"Uma solicitação mudou de status e requer sua atenção.\n\n"
                f"Detalhes da solicitação:\n"
                f"- Status: {event_key}\n"
                f"- ID: {row_data.get('Id', 'N/A')}\n"
                f"- Solicitante: {row_data.get('Nome completo (sem abreviações):', 'N/A')}\n"
                f"- CPF: {row_data.get('CPF:', 'N/A')}\n"
                f"- Valor: R$ {row_data.get('Valor', '0,00')}\n"
                f"- Motivo: {row_data.get('Motivo da solicitação', 'N/A')}\n"
                f"- Data da solicitação: {row_data.get('Carimbo de data/hora', 'N/A')}\n\n"
                f"Por favor, acesse o sistema para verificar os detalhes completos e tomar as ações necessárias.\n\n"
                f"Atenciosamente,\nSistema Financeiro"
            )

            body_text.insert('1.0', body)
            body_text.config(state='disabled')

            def send_notifications():
                success = False
                for email in recipients:
                    if email and email.strip():
                        try:
                            self.app.email_sender.send_email(email.strip(), subject, body)
                            logger_app.log_info(f"Email de notificação enviado para {email.strip()} - evento: {event_key}")
                            success = True
                        except Exception as e:
                            logger_app.log_error(f"Erro ao enviar email para {email.strip()}: {str(e)})")
                
                if success:
                    logger_app.log_info(f"Notificações enviadas com sucesso para o evento {event_key}")
                    messagebox.showinfo("Sucesso", "Emails de notificação enviados com sucesso!")
                else:
                    logger_app.log_warning(f"Nenhuma notificação enviada para o evento {event_key}")
                    messagebox.showwarning("Aviso", "Não foi possível enviar os emails de notificação")
                
                preview_window.destroy()

            btn_frame = tb.Frame(preview_window)
            btn_frame.pack(pady=10)

            send_btn = tb.Button(btn_frame, text="Enviar Notificações", bootstyle=SUCCESS, command=send_notifications)
            send_btn.pack(side=LEFT, padx=5)

            cancel_btn = tb.Button(btn_frame, text="Cancelar", bootstyle=DANGER, command=preview_window.destroy)
            cancel_btn.pack(side=LEFT, padx=5)

        except Exception as e:
            logger_app.log_error(f"Erro ao processar notificações: {str(e)}")
            messagebox.showerror("Erro", "Erro ao processar notificações")

    def add_actions_tab(self, notebook, row_data):
        view = self.app.current_view
        role = self.app.user_role
        actions_tab = tb.Frame(notebook)
        notebook.add(actions_tab, text="Ações")

        if view == "Aceitas":
            def request_documents():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Permissão Negada", "Apenas A3 ou A5.")
                    return
                new_status = 'Aguardando documentação'
                ts_str = row_data['Carimbo de data/hora']
                self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name)

                motivo = row_data.get('Motivo da solicitação', 'Outros').strip()
                email_template = self.app.email_templates.get(motivo, self.app.email_templates['Outros'])
                subject = "Requisição de Documentos"
                body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                self.app.update_table()
                self.app.go_to_home()
                
            def cancel_auxilio():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Negado", "Somente A3 ou A5 podem cancelar.")
                    return
                confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja recusar/cancelar o auxílio?")
                if confirm:
                    new_status = 'Cancelado'
                    ts_str = row_data['Carimbo de data/hora']
                    if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                        # Primeiro notifica os responsáveis
                        self.ask_send_notification_emails("Cancelado", row_data)
                        
                        # Depois envia email para o solicitante
                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.app.update_table()
                        self.app.go_to_home()
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar status")

            def authorize_payment():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Permissão Negada", "Somente A3 ou A5.")
                    return
                new_status = 'Pronto para pagamento'
                ts_str = row_data['Carimbo de data/hora']
                if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                    # Primeiro notifica os responsáveis
                    self.ask_send_notification_emails("ProntoPagamento", row_data)
                    
                    # Depois envia email para o solicitante
                    email_template = self.app.email_templates.get('Aprovação', 'Sua solicitação foi aprovada.')
                    subject = "Pagamento Autorizado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.go_to_home()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar status")

            req_btn = tb.Button(actions_tab, text="Requerir Documentos", bootstyle=WARNING, command=request_documents)
            req_btn.pack(pady=10)

            cancel_btn = tb.Button(actions_tab, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=cancel_auxilio)
            cancel_btn.pack(pady=10)

            auth_btn = tb.Button(actions_tab, text="Autorizar Pagamento", bootstyle=SUCCESS, command=authorize_payment)
            auth_btn.pack(pady=10)
        
        elif view == "Aguardando documentos":
            
            def request_documents():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Permissão Negada", "Apenas A3 ou A5.")
                    return
                new_status = 'Aguardando documentação'
                ts_str = row_data['Carimbo de data/hora']
                self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name)

                motivo = row_data.get('Motivo da solicitação', 'Outros').strip()
                email_template = self.app.email_templates.get(motivo, self.app.email_templates['Outros'])
                subject = "Requisição de Documentos"
                body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                self.app.update_table()
                self.app.go_to_home()

            def authorize_payment():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Permissão Negada", "Somente A3 ou A5.")
                    return
                new_status = 'Pronto para pagamento'
                ts_str = row_data['Carimbo de data/hora']
                if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                    # Primeiro notifica os responsáveis
                    self.ask_send_notification_emails("ProntoPagamento", row_data)
                    
                    # Depois envia email para o solicitante
                    email_template = self.app.email_templates.get('Aprovação', 'Sua solicitação foi aprovada.')
                    subject = "Pagamento Autorizado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.go_to_home()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar status")

            def cancel_auxilio():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Negado", "Somente A3 ou A5 podem cancelar.")
                    return
                confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja recusar/cancelar o auxílio?")
                if confirm:
                    new_status = 'Cancelado'
                    ts_str = row_data['Carimbo de data/hora']
                    if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                        # Primeiro notifica os responsáveis
                        self.ask_send_notification_emails("Cancelado", row_data)
                        
                        # Depois envia email para o solicitante
                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.app.update_table()
                        self.app.go_to_home()
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar status")

            req_btn = tb.Button(actions_tab, text="Requerir Documentos", bootstyle=WARNING, command=request_documents)
            req_btn.pack(pady=10)

            auth_btn = tb.Button(actions_tab, text="Autorizar Pagamento", bootstyle=SUCCESS, command=authorize_payment)
            auth_btn.pack(pady=10)

            cancel_btn = tb.Button(actions_tab, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=cancel_auxilio)
            cancel_btn.pack(pady=10)

        elif view == "Pronto para pagamento":
            def payment_made():
                if role not in ["A3", "A4", "A5"]:
                    messagebox.showwarning("Negado", "Você não tem permissão de efetuar pagamento.")
                    return
                new_status = 'Pago'
                ts_str = row_data['Carimbo de data/hora']
                if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                    # Primeiro notifica os responsáveis (opcional para pagamento)
                    self.ask_send_notification_emails("Pago", row_data)
                    
                    # Depois envia email para o solicitante
                    email_template = self.app.email_templates.get('Pagamento', 'Seu pagamento foi efetuado.')
                    subject = "Pagamento Efetuado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.back_to_main_view()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar status")

            def cancel_auxilio():
                if role not in ["A3", "A5"]:
                    messagebox.showwarning("Permissão Negada", "Apenas A3 ou A5 podem cancelar.")
                    return
                confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                if confirm:
                    new_status = 'Cancelado'
                    ts_str = row_data['Carimbo de data/hora']
                    if self.app.sheets_handler.update_status(ts_str, new_status, self.app.user_name):
                        # Primeiro notifica os responsáveis
                        self.ask_send_notification_emails("Cancelado", row_data)
                        
                        # Depois envia email para o solicitante
                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.app.update_table()
                        self.app.back_to_main_view()
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar status")

            payment_btn = tb.Button(actions_tab, text="Pagamento Efetuado", bootstyle=SUCCESS, command=payment_made)
            payment_btn.pack(pady=10)

            cancel_btn = tb.Button(actions_tab, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=cancel_auxilio)
            cancel_btn.pack(pady=10)

    def show_details_in_new_window(self, row_data):
        detail_window = tb.Toplevel(self.app.root)
        detail_window.title("Detalhes da Solicitação")
        detail_window.geometry("800x600")

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

    def ask_send_email(self, row_data, new_status, new_value=None):
        confirm = messagebox.askyesno("Enviar E-mail", "Deseja enviar um e-mail notificando a alteração de status?")
        if confirm:
            email_window = tb.Toplevel(self.app.root)
            email_window.title("Enviar E-mail")

            recipient_label = tb.Label(email_window, text="Destinatário:")
            recipient_label.pack(anchor="w", padx=10, pady=5)
            recipient_email = row_data['Endereço de e-mail']
            recipient_entry = tb.Entry(email_window, width=50)
            recipient_entry.insert(0, recipient_email)
            recipient_entry.pack(anchor="w", padx=10, pady=5)

            email_body_label = tb.Label(email_window, text="Corpo do E-mail:")
            email_body_label.pack(anchor="w", padx=10, pady=5)

            body_text = tb.ScrolledText(email_window, width=60, height=15)
            body_text.pack(anchor="w", padx=10, pady=5)

            body = f"Olá {row_data['Nome completo (sem abreviações):']},\n\n" \
                   f"Seu status foi alterado para: {new_status}."
            if new_value:
                body += f"\nValor do auxílio: R$ {new_value}."

            body += f"\nCurso: {row_data['Curso:']}.\nOrientador: {row_data['Orientador']}."
            body += "\n\nAtt,\nEquipe de Suporte"

            body_text.insert('1.0', body)

            def send_email_action():
                recipient = recipient_entry.get().strip()
                subject = "Atualização de Status"
                content = body_text.get("1.0", "end")
                self.app.email_sender.send_email(recipient, subject, content)
                email_window.destroy()

            send_button = tb.Button(email_window, text="Enviar E-mail", bootstyle=SUCCESS, command=send_email_action)
            send_button.pack(pady=10)

    def send_custom_email(self, recipient, subject, body):
        email_window = tb.Toplevel(self.app.root)
        email_window.title("Enviar E-mail")

        recipient_label = tb.Label(email_window, text="Destinatário:")
        recipient_label.pack(anchor="w", padx=10, pady=5)
        recipient_entry = tb.Entry(email_window, width=50)
        recipient_entry.insert(0, recipient)
        recipient_entry.pack(anchor="w", padx=10, pady=5)

        email_body_label = tb.Label(email_window, text="Corpo do E-mail:")
        email_body_label.pack(anchor="w", padx=10, pady=5)

        body_text = tb.ScrolledText(email_window, width=60, height=15)
        body_text.pack(anchor="w", padx=10, pady=5)
        body_text.insert('1.0', body)

        def send_email_action():
            recipient_addr = recipient_entry.get().strip()
            email_body = body_text.get("1.0", "end")
            self.app.email_sender.send_email(recipient_addr, subject, email_body)
            email_window.destroy()

        send_button = tb.Button(email_window, text="Enviar E-mail", bootstyle=SUCCESS, command=send_email_action)
        send_button.pack(pady=10)

    def toggle_edit_mode(self, row_data):
        if not self.edit_mode:
            # Entrando no modo de edição
            self.original_text = self.obs_text.get('1.0', 'end-1c')
            self.obs_text.config(state='normal')
            self.edit_btn.config(state='disabled')
            self.confirm_btn.config(state='normal')
            self.cancel_btn.config(state='normal')
            self.edit_mode = True
        
    def save_observations(self, row_data):
        new_text = self.obs_text.get('1.0', 'end-1c')
        ts_str = row_data['Carimbo de data/hora']
        
        # Atualizar no Google Sheets
        self.app.sheets_handler.update_observations(ts_str, new_text)
        
        # Desabilitar edição
        self.obs_text.config(state='disabled')
        self.edit_btn.config(state='normal')
        self.confirm_btn.config(state='disabled')
        self.cancel_btn.config(state='disabled')
        self.edit_mode = False
        
        messagebox.showinfo("Sucesso", "Observações atualizadas com sucesso!")
        
    def cancel_edit(self):
        # Restaurar texto original
        self.obs_text.delete('1.0', 'end')
        self.obs_text.insert('1.0', self.original_text)
        
        # Desabilitar edição
        self.obs_text.config(state='disabled')
        self.edit_btn.config(state='normal')
        self.confirm_btn.config(state='disabled')
        self.cancel_btn.config(state='disabled')
        self.edit_mode = False
