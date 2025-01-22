# details_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Text, messagebox
from datetime import datetime

# Mapeamento de colunas do forms -> máscaras
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
    'Possui bolsa?': 'Possui Bolsa?',
    'Qual a agência de fomento?': 'Agência de Fomento',
    'Título do projeto do qual participa:': 'Título do Projeto',
    'Motivo da solicitação': 'Motivo do Pedido',
    'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A':
        'Nome do Evento/Atividade',
    'Local de realização do evento': 'Local do Evento',
    'Período de realização da atividade. Indique as datas (dd/mm/aaaa)': 'Período da Atividade',
    'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias ...':
        'Itens a Financiar',
    'Valor': 'Valor Solicitado (R$)',
    'Dados bancários (banco, agência e conta) ': 'Dados Bancários'
}

class DetailsManager:
    def __init__(self, app):
        self.app = app
        # Vinculamos o dicionário global
        self.FORM_FIELD_MAPPING = FORM_FIELD_MAPPING

    def show_details_in_place(self, row_data):
        """
        Cria Notebook com:
          - Informações Pessoais
          - Informações Acadêmicas
          - Detalhes da Solicitação
          - Informações Financeiras
          - (Histórico)
          - (Ações)
        A aba 'Histórico' vem antes da 'Ações'. Alinhamento sticky='w'.
        """
        # Esconder tabela
        self.app.table_frame.pack_forget()

        self.app.details_frame = tb.Frame(self.app.content_frame)
        self.app.details_frame.pack(fill=BOTH, expand=True)

        self.app.details_title_label = tb.Label(
            self.app.details_frame,
            text="Controle de Orçamento IG - PPG UNICAMP",
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
                'Motivo da solicitação',
                'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
                'Local de realização do evento',
                'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
                'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias ...',
            ],
            "Informações Financeiras": [
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        # Criar 4 abas principais
        for section_name, fields in sections.items():
            tab_frame = tb.Frame(notebook)
            notebook.add(tab_frame, text=section_name)

            tab_frame.columnconfigure(0, weight=1, minsize=200)
            tab_frame.columnconfigure(1, weight=3)

            row_idx = 0
            for col in fields:
                if col in row_data:
                    display_label = self.FORM_FIELD_MAPPING.get(col, col)
                    label = tb.Label(tab_frame, text=f"{display_label}:", font=("Helvetica", 12, "bold"))
                    label.grid(row=row_idx, column=0, sticky='w', padx=10, pady=5)

                    value_text = str(row_data[col])
                    value = tb.Label(tab_frame, text=value_text, font=("Helvetica", 12))
                    value.grid(row=row_idx, column=1, sticky='w', padx=10, pady=5)
                    row_idx += 1

            # Se for aba Financeira e status=''
            if section_name == "Informações Financeiras" and row_data['Status'] == '':
                value_label = tb.Label(tab_frame, text="Valor (R$):", font=("Helvetica", 12, "bold"))
                value_label.grid(row=row_idx, column=0, sticky='w', padx=10, pady=5)
                value_entry = tb.Entry(tab_frame, width=50)
                value_entry.grid(row=row_idx, column=1, sticky='w', padx=10, pady=5)
                self.app.value_entry = value_entry

                row_idx += 1

                def autorizar_auxilio():
                    new_value = self.app.value_entry.get().strip()
                    if not new_value:
                        messagebox.showwarning("Aviso", "Por favor, insira um valor.")
                        return
                    new_status = 'Autorizado'
                    timestamp_str = row_data['Carimbo de data/hora']
                    self.app.sheets_handler.update_status(timestamp_str, new_status)
                    self.app.sheets_handler.update_value(timestamp_str, new_value)
                    self.ask_send_email(row_data, new_status, new_value)
                    self.app.update_table()
                    self.app.back_to_main_view()

                def negar_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora']
                        self.app.sheets_handler.update_status(timestamp_str, new_status)
                        self.ask_send_email(row_data, new_status)
                        self.app.update_table()
                        self.app.back_to_main_view()

                autorizar_button = tb.Button(
                    tab_frame,
                    text="Autorizar Auxílio",
                    bootstyle=SUCCESS,
                    command=autorizar_auxilio
                )
                negar_button = tb.Button(
                    tab_frame,
                    text="Recusar/Cancelar Auxílio",
                    bootstyle=DANGER,
                    command=negar_auxilio
                )
                autorizar_button.grid(row=row_idx, column=0, padx=10, pady=10, sticky='w')
                negar_button.grid(row=row_idx, column=1, padx=10, pady=10, sticky='w')

        # Adicionar aba histórico antes de ações
        self.add_history_tab(notebook, row_data)
        self.add_actions_tab(notebook, row_data)

        self.app.back_button.pack(side='bottom', pady=20)

    def add_history_tab(self, notebook, row_data):
        history_tab = tb.Frame(notebook)
        # Aba "Histórico de Solicitações"
        notebook.add(history_tab, text="Histórico de Solicitações")

        cpf = str(row_data.get('CPF:', '')).strip()
        all_data = self.app.sheets_handler.load_data()
        all_data['CPF:'] = all_data['CPF:'].astype(str).str.strip()
        history_data = all_data[all_data['CPF:'] == cpf]

        history_columns = ['Carimbo de data/hora', 'Ultima Atualizacao', 'Valor', 'Status']
        history_tree = tb.Treeview(history_tab, columns=history_columns, show='headings', height=10)
        history_tree.pack(fill=BOTH, expand=True)

        for col in history_columns:
            history_tree.heading(
                col,
                text=col,
                command=lambda _col=col: self.app.treeview_sort_column(history_tree, _col, False)
            )
            history_tree.column(col, anchor='center', width=120)

        self.app.history_tree_data = history_data.copy()

        for idx, hist_row in history_data.iterrows():
            values = [hist_row[col] for col in history_columns]
            history_tree.insert("", "end", iid=str(idx), values=values)

        history_tree.bind("<Double-1>", self.on_history_treeview_click)

    def add_actions_tab(self, notebook, row_data):
        # Só adiciona se for Pendências ou Pronto para pagamento
        if self.app.current_view in ["Pendências", "Pronto para pagamento"]:
            actions_tab = tb.Frame(notebook)
            notebook.add(actions_tab, text="Ações")

            if self.app.current_view == "Pendências":
                def request_documents():
                    new_status = 'Aguardando documentação'
                    timestamp_str = row_data['Carimbo de data/hora']
                    self.app.sheets_handler.update_status(timestamp_str, new_status)

                    motivo = row_data.get('Motivo da solicitação', 'Outros').strip()
                    email_template = self.app.email_templates.get(motivo, self.app.email_templates['Outros'])
                    subject = "Requisição de Documentos"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.back_to_main_view()

                def authorize_payment():
                    new_status = 'Pronto para pagamento'
                    timestamp_str = row_data['Carimbo de data/hora']
                    self.app.sheets_handler.update_status(timestamp_str, new_status)

                    email_template = self.app.email_templates.get('Aprovação', 'Sua solicitação foi aprovada.')
                    subject = "Pagamento Autorizado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.back_to_main_view()

                def cancel_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora']
                        self.app.sheets_handler.update_status(timestamp_str, new_status)

                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.app.update_table()
                        self.app.back_to_main_view()

                request_button = tb.Button(actions_tab, text="Requerir Documentos", bootstyle=WARNING, command=request_documents)
                request_button.pack(pady=10)

                authorize_button = tb.Button(actions_tab, text="Autorizar Pagamento", bootstyle=SUCCESS, command=authorize_payment)
                authorize_button.pack(pady=10)

                cancel_button = tb.Button(actions_tab, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=cancel_auxilio)
                cancel_button.pack(pady=10)

            elif self.app.current_view == "Pronto para pagamento":
                def payment_made():
                    new_status = 'Pago'
                    timestamp_str = row_data['Carimbo de data/hora']
                    self.app.sheets_handler.update_status(timestamp_str, new_status)

                    email_template = self.app.email_templates.get('Pagamento', 'Seu pagamento foi efetuado.')
                    subject = "Pagamento Efetuado"
                    body = email_template.format(Nome=row_data['Nome completo (sem abreviações):'])
                    self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                    self.app.update_table()
                    self.app.back_to_main_view()

                def cancel_auxilio():
                    confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja recusar/cancelar o auxílio?")
                    if confirm:
                        new_status = 'Cancelado'
                        timestamp_str = row_data['Carimbo de data/hora']
                        self.app.sheets_handler.update_status(timestamp_str, new_status)

                        subject = "Auxílio Cancelado"
                        body = (
                            f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                            f"Seu auxílio foi cancelado.\n\n"
                            f"Atenciosamente,\nEquipe Financeira"
                        )
                        self.send_custom_email(row_data['Endereço de e-mail'], subject, body)
                        self.app.update_table()
                        self.app.back_to_main_view()

                payment_button = tb.Button(actions_tab, text="Pagamento Efetuado", bootstyle=SUCCESS, command=payment_made)
                payment_button.pack(pady=10)

                cancel_button = tb.Button(actions_tab, text="Recusar/Cancelar Auxílio", bootstyle=DANGER, command=cancel_auxilio)
                cancel_button.pack(pady=10)

    def on_history_treeview_click(self, event):
        selected_item = event.widget.selection()
        if selected_item:
            item_iid = selected_item[0]
            selected_row = self.app.history_tree_data.loc[int(item_iid)]
            self.show_details_in_new_window(selected_row)

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

        # Repetir as abas (sem botões de autorizar)
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
                'Descrever detalhadamente os itens a serem financiados...',
            ],
            "Informações Financeiras": [
                'Valor',
                'Dados bancários (banco, agência e conta) ',
            ],
        }

        for section_name, fields in sections.items():
            tab_frame = tb.Frame(notebook)
            notebook.add(tab_frame, text=section_name)

            tab_frame.columnconfigure(0, weight=1, minsize=200)
            tab_frame.columnconfigure(1, weight=3)

            row_idx = 0
            for col in fields:
                if col in row_data:
                    display_label = self.FORM_FIELD_MAPPING.get(col, col)
                    label = tb.Label(tab_frame, text=f"{display_label}:", font=("Helvetica", 12, "bold"))
                    label.grid(row=row_idx, column=0, sticky='w', padx=10, pady=5)

                    value_text = str(row_data[col])
                    value = tb.Label(tab_frame, text=value_text, font=("Helvetica", 12))
                    value.grid(row=row_idx, column=1, sticky='w', padx=10, pady=5)
                    row_idx += 1

        close_button = tb.Button(detail_frame, text="Fechar", bootstyle=PRIMARY, command=detail_window.destroy)
        close_button.pack(pady=10)

    # Métodos de e-mail
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

            body = (
                f"Olá {row_data['Nome completo (sem abreviações):']},\n\n"
                f"Seu status foi alterado para: {new_status}."
            )
            if new_value:
                body += f"\nValor do auxílio: R$ {new_value}."

            body += (
                f"\nCurso: {row_data['Curso:']}.\nOrientador: {row_data['Orientador']}."
                f"\n\nAtt,\nEquipe de Suporte"
            )
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
