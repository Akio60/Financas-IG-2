# settings_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from machine_manager import MachineManager
from tkinter import messagebox
import json
import os
import hashlib
from datetime import datetime
import logger_app
import re

BTN_WIDTH = 35

USERS_DB_FILE = "users_db.json"

# Tamanhos padrão de janelas
WINDOW_SIZES = {
    'settings': (600, 520),  # Aumentado em 40px
    'column_selector': (600, 520),  # Aumentado em 40px 
    'user_manager': (600, 520),  # Aumentado em 40px
    'add_user': (600, 520),  # Aumentado em 40px
    'email_template': (600, 520),  # Aumentado em 40px
    'notification': (600, 520),  # Aumentado em 40px
    'add_email': (400, 150),  # Mantido mesmo tamanho
    'machine_manager': (600, 520)  # Nova janela
}

def load_users_db():
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users_db(db):
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def hash_password(password):
    """Retorna o hash SHA-256 da senha fornecida."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class SettingsManager:
    # Atualizar o dicionário de cargos para ter apenas A1, A3 e A5
    ROLE_NAMES = {
        "A1": "Visualizador",
        "A3": "Editor",
        "A5": "Administrador"
    }

    def __init__(self, app):
        self.app = app
        self.settings_window = None
        self.mask_window = None

        self.users_db = load_users_db()

    def _prevent_resize_maximize(self, window):
        """Impede redimensionamento e maximização da janela"""
        window.resizable(False, False)
        window.attributes('-toolwindow', True)

    def _center_window(self, window, w, h):
        """Centraliza qualquer janela"""
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        window.geometry(f"{w}x{h}+{x}+{y}")

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tb.Toplevel(self.app.root)
        self.settings_window.title("Configurações")
        w, h = WINDOW_SIZES['settings']
        self._center_window(self.settings_window, w, h)
        self._prevent_resize_maximize(self.settings_window)
        self.settings_window.attributes('-topmost', True)  # Adiciona sempre no topo

        main_frame = tb.Frame(self.settings_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        col1 = tb.Frame(main_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        col1.columnconfigure(0, weight=1)

        instructions_label = tb.Label(
            col1,
            text="Configurações",
            font=("Helvetica", 12, "bold")
        )
        instructions_label.grid(row=0, column=0, sticky='w', pady=5)



        if self.app.user_role == "A5":
            
            user_btn = tb.Button(
                col1,
                text="Cadastrar/Remover Usuários",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.user_management
            )
            user_btn.grid(row=1, column=0, sticky='w', pady=10)

            notif_btn = tb.Button(
                col1,
                text="Email de notificação por status",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.setup_notification_cargos
            )
            notif_btn.grid(row=2, column=0, sticky='w', pady=10)

            history_btn = tb.Button(
                col1,
                text="Histórico de alterações",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.show_logs
            )
            history_btn.grid(row=3, column=0, sticky='w', pady=10)
            
            machine_btn = tb.Button(
                col1,
                text="Gerenciar Máquinas Autorizadas",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.manage_machines
            )
            machine_btn.grid(row=4, column=0, sticky='w', pady=10)
            
            row_start_col = 5  # Começa do 5 para A5
        else:
            history_btn = tb.Button(  # Apenas histórico disponível para A3
                col1,
                text="Histórico de alterações",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.show_logs
            )
            history_btn.grid(row=1, column=0, sticky='w', pady=10)
            
            row_start_col = 2  # Começa do 2 para A3

        columns_label = tb.Label(col1, text="Definição de Colunas", font=("Helvetica", 10, "bold"))
        columns_label.grid(row=row_start_col, column=0, sticky='w', pady=(15,5))
        row_start_col += 1

        col_txt = (
            "Selecione quais colunas serão exibidas em cada visualização\n"
            "e defina a ordem delas."
        )
        col_info_label = tb.Label(col1, text=col_txt, font=("Helvetica", 9), foreground="gray", wraplength=300)
        col_info_label.grid(row=row_start_col, column=0, sticky='w', pady=5)
        row_start_col += 1

        views = [
            ("Solicitações Recebidas", "Aguardando aprovação"),
            ("Solicitações Aceitas", "Aceitas"),
            ("Aguardando documentos", "Aguardando documentos"),
            ("Pronto para pagamento", "Pronto para pagamento")
        ]
        row_index = row_start_col
        for label_text, view_name in views:
            btn = tb.Button(
                col1,
                text=label_text,
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=lambda v=view_name: self.open_column_selector(v)
            )
            btn.grid(row=row_index, column=0, sticky='w', pady=5)
            row_index += 1

        col1.rowconfigure(row_index, weight=1)

        col2 = tb.Frame(main_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        col2.columnconfigure(0, weight=1)

        email_section_label = tb.Label(col2, text="E-mails:", font=("Helvetica", 12, "bold"))
        email_section_label.grid(row=0, column=0, sticky='w', pady=5)

        infobox_text = (
            "Use chaves {} para inserir dados do formulário.\n"
            "Ex.: {Nome}, {CPF:}, {Telefone de contato:}, etc."
        )
        infobox_label = tb.Label(col2, text=infobox_text, font=("Helvetica", 9), foreground="gray", wraplength=300)
        infobox_label.grid(row=1, column=0, sticky='w', pady=5)

        # Lista completa de todos os templates disponíveis
        templates_order = [
            "Trabalho de Campo",
            "Participação em eventos",
            "Visita técnica",
            "Outros",
            "Aprovação",
            "Pagamento",
            "Cancelamento", 
            "ProntoPagamento",
            "AguardandoDocumentacao"
        ]

        row_index2 = 2
        for template_name in templates_order:
            button = tb.Button(
                col2, 
                text=f"{template_name}", 
                bootstyle=SECONDARY,
                width=BTN_WIDTH,
                command=lambda t=template_name: self.edit_email_template(t)
            )
            button.grid(row=row_index2, column=0, sticky='w', pady=5)
            row_index2 += 1

        col2.rowconfigure(row_index2, weight=1)

    def open_column_selector(self, view_name):
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Colunas - {view_name}")
        w, h = WINDOW_SIZES['column_selector']
        self._center_window(sel_window, w, h)
        self._prevent_resize_maximize(sel_window)
        sel_window.attributes('-topmost', True)  # Adiciona sempre no topo

        top_label = tb.Label(sel_window, text=f"Colunas para: {view_name}", font=("Helvetica", 11, "bold"))
        top_label.pack(pady=5)

        container = tb.Frame(sel_window)
        container.pack(fill="both", expand=True)

        all_possible = [
            'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
            'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
            'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
            'Telefone de contato:', 'Carimbo de data/hora_str', 'Status', 'Ultima Atualizacao', 'Valor',
            'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
            'RG/RNE:', 'Dados bancários (banco, agência e conta) ', 'Valor solicitado. Somente valor, sem pontos e vírgula','Ultima modificação'
        ]
        current_cols = self.app.custom_views.get(view_name, [])

        left_frame = tb.Frame(container)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        lbl_left = tb.Label(left_frame, text="Disponíveis", font=("Helvetica", 10, "bold"))
        lbl_left.pack(pady=5)

        import tkinter as tki
        list_avail = tki.Listbox(left_frame, selectmode='extended')
        list_avail.pack(fill="both", expand=True)

        center_frame = tb.Frame(container)
        center_frame.pack(side="left", pady=5)

        right_frame = tb.Frame(container)
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        lbl_right = tb.Label(right_frame, text="Selecionadas (ordem)", font=("Helvetica", 10, "bold"))
        lbl_right.pack(pady=5)

        list_select = tki.Listbox(right_frame, selectmode='extended')
        list_select.pack(fill="both", expand=True)

        def load_lists():
            list_avail.delete(0, 'end')
            list_select.delete(0, 'end')
            for col in all_possible:
                if col not in current_cols:
                    list_avail.insert('end', col)
            for col in current_cols:
                list_select.insert('end', col)

        def move_to_selected():
            sel = list_avail.curselection()
            if not sel:
                return
            items = [list_avail.get(i) for i in sel]
            for it in items:
                if it not in current_cols:
                    current_cols.append(it)
            load_lists()

        def move_to_available():
            sel = list_select.curselection()
            if not sel:
                return
            items = [list_select.get(i) for i in sel]
            for it in items:
                if it in current_cols:
                    current_cols.remove(it)
            load_lists()

        def move_up():
            sel = list_select.curselection()
            if not sel:
                return
            for index in sel:
                if index == 0:
                    continue
                current_cols[index], current_cols[index-1] = current_cols[index-1], current_cols[index]
            load_lists()
            for i, idx in enumerate(sel):
                new_idx = idx - 1 if idx > 0 else 0
                list_select.selection_set(new_idx)

        def move_down():
            sel = list_select.curselection()
            if not sel:
                return
            for index in reversed(sel):
                if index >= len(current_cols)-1:
                    continue
                current_cols[index], current_cols[index+1] = current_cols[index+1], current_cols[index]
            load_lists()
            for i, idx in enumerate(sel):
                new_idx = idx + 1 if idx < len(current_cols)-1 else idx
                list_select.selection_set(new_idx)

        btn_add = tb.Button(center_frame, text="->", bootstyle=SUCCESS, command=move_to_selected)
        btn_add.pack(padx=5, pady=10)
        btn_remove = tb.Button(center_frame, text="<-", bootstyle=DANGER, command=move_to_available)
        btn_remove.pack(padx=5, pady=10)

        btn_up = tb.Button(center_frame, text="▲", bootstyle=INFO, command=move_up)
        btn_up.pack(padx=5, pady=10)
        btn_down = tb.Button(center_frame, text="▼", bootstyle=INFO, command=move_down)
        btn_down.pack(padx=5, pady=10)

        load_lists()

        def close_and_save():
            self.app.custom_views[view_name] = current_cols
            sel_window.destroy()

        close_btn = tb.Button(sel_window, text="Salvar", bootstyle=SUCCESS, width=BTN_WIDTH, command=close_and_save)
        close_btn.pack(pady=10)

    def edit_email_template(self, motivo):
        template_window = tb.Toplevel(self.app.root)
        template_window.title(motivo)
        w, h = WINDOW_SIZES['email_template']
        self._center_window(template_window, w, h)
        self._prevent_resize_maximize(template_window)
        template_window.attributes('-topmost', True)  # Adiciona sempre no topo

        label = tb.Label(template_window, text=f"Modelo de E-mail: {motivo}", font=("Helvetica", 12))
        label.pack(pady=10)

        frame = tb.Frame(template_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        text_widget = tb.ScrolledText(frame, width=70, height=15)
        text_widget.pack(fill="both", expand=True, side="top")

        save_button = tb.Button(frame, text="Salvar", bootstyle=SUCCESS, width=BTN_WIDTH, command=lambda: save_template(template_window, text_widget, motivo))
        save_button.pack(side="bottom", pady=10)

        text_widget.insert('1.0', self.app.email_templates[motivo])

        def save_template(window, text_widget, motivo):
            new_template = text_widget.get("1.0", 'end').strip()
            self.app.email_templates[motivo] = new_template
            self.app.save_email_templates()
            window.destroy()

    def user_management(self):
        um_window = tb.Toplevel(self.app.root)
        um_window.title("Gerenciar Usuários")
        w, h = WINDOW_SIZES['user_manager']
        self._center_window(um_window, w, h)
        self._prevent_resize_maximize(um_window)
        um_window.attributes('-topmost', True)  # Adiciona sempre no topo

        db_users = load_users_db()

        tk.Label(um_window, text="Usuários Cadastrados:", font=("Helvetica", 12, "bold")).pack(pady=5)

        listbox = tk.Listbox(um_window)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        def refresh_users():
            listbox.delete(0, 'end')
            for u in db_users.keys():
                r = db_users[u]["role"]
                e = db_users[u]["email"]
                listbox.insert('end', f"{u} | Cargo: {r} | Email: {e}")

        refresh_users()

        btn_frame = tk.Frame(um_window)
        btn_frame.pack(pady=5)

        def add_user():
            def confirm_add():
                try:
                    # Validação dos campos
                    if not all([login_var.get(), name_var.get(), pass_var.get(), email_var.get()]):
                        error_window = tb.Toplevel()
                        error_window.title("Erro")
                        error_window.attributes('-topmost', True)  # Força janela de erro ficar no topo
                        w, h = 300, 100
                        self._center_window(error_window, w, h)
                        self._prevent_resize_maximize(error_window)
                        
                        tb.Label(error_window, text="Todos os campos são obrigatórios.", padding=20).pack()
                        tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
                        return
                    
                    # Validação de email
                    email = email_var.get().strip()
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                        error_window = tb.Toplevel()
                        error_window.title("Erro")
                        error_window.attributes('-topmost', True)
                        w, h = 300, 100
                        self._center_window(error_window, w, h)
                        self._prevent_resize_maximize(error_window)
                        
                        tb.Label(error_window, text="Email inválido!", padding=20).pack()
                        tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
                        return
                    
                    if email != confirm_email_var.get().strip():
                        error_window = tb.Toplevel()
                        error_window.title("Erro")
                        error_window.attributes('-topmost', True)
                        w, h = 300, 100
                        self._center_window(error_window, w, h)
                        self._prevent_resize_maximize(error_window)
                        
                        tb.Label(error_window, text="Os emails não coincidem!", padding=20).pack()
                        tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
                        return

                    # Validação de senha
                    if pass_var.get() != confirm_pass_var.get():
                        error_window = tb.Toplevel()
                        error_window.title("Erro")
                        error_window.attributes('-topmost', True)
                        w, h = 300, 100
                        self._center_window(error_window, w, h)
                        self._prevent_resize_maximize(error_window)
                        
                        tb.Label(error_window, text="As senhas não coincidem!", padding=20).pack()
                        tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
                        return

                    login = login_var.get().strip()
                    if login in db_users:
                        error_window = tb.Toplevel()
                        error_window.title("Erro")
                        error_window.attributes('-topmost', True)
                        w, h = 300, 100
                        self._center_window(error_window, w, h)
                        self._prevent_resize_maximize(error_window)
                        
                        tb.Label(error_window, text="Login já existe!", padding=20).pack()
                        tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
                        return

                    # Prepara dados do usuário
                    user_data = {
                        "name": name_var.get().strip(),
                        "login": login,
                        "hashed_password": hash_password(pass_var.get() + login),
                        "role": role_var.get(),
                        "email": email,
                        "role_name": self.ROLE_NAMES[role_var.get()]
                    }

                    # Salva primeiro no banco de dados
                    db_users[login] = user_data
                    save_users_db(db_users)
                    logger_app.append_log(
                        logger_app.LogLevel.INFO,
                        logger_app.LogCategory.USER_ACTION,
                        "SYSTEM",
                        "CREATE_USER",
                        f"Novo usuário criado: {login}"
                    )

                    # Prepara emails
                    user_email = {
                        "recipient": email,
                        "subject": "Bem-vindo ao Sistema Financeiro IG",
                        "body": f"""
Olá {user_data['name']},

Sua conta foi criada no Sistema Financeiro IG com as seguintes informações:

Login: {user_data['login']}
Cargo: {user_data['role']} - {user_data['role_name']}

Você já pode acessar o sistema usando seu login e a senha cadastrada.

Atenciosamente,
Equipe do Sistema Financeiro IG""",
                        "type": "Novo Usuário"
                    }

                    # Obtém emails dos administradores da planilha
                    admin_emails = self.app.sheets_handler.get_notification_emails().get('ADMIN', [])
                    if not admin_emails:
                        logger_app.append_log(
                            logger_app.LogLevel.INFO,
                            logger_app.LogCategory.SYSTEM,
                            "SYSTEM",
                            "WARNING",
                            "Nenhum email de administrador configurado na aba Email, coluna ADMIN"
                        )
                        messagebox.showwarning(
                            "Atenção", 
                            "Não foi possível notificar administradores (configure os emails na aba Email, coluna ADMIN)"
                        )

                    admin_notifications = []
                    for admin_email in admin_emails:
                        admin_notifications.append({
                            "recipient": admin_email.strip(),
                            "subject": "Novo Usuário Cadastrado - Sistema Financeiro IG",
                            "body": f"""
Um novo usuário foi cadastrado no sistema:

Nome: {user_data['name']}
Login: {user_data['login']}
Email: {user_data['email']}
Cargo: {user_data['role']} - {user_data['role_name']}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Este é um email automático de notificação.""",
                            "type": "Notificação Admin"
                        })

                    # Lista completa de emails para enviar
                    emails_to_send = [user_email] + admin_notifications

                    # Cria janela de progresso
                    progress_window = tb.Toplevel(addw)
                    progress_window.title("Enviando Emails")
                    w, h = 400, 300
                    self._center_window(progress_window, w, h)
                    self._prevent_resize_maximize(progress_window)
                    progress_window.attributes('-topmost', True)  # Adiciona sempre no topo

                    # Configura elementos visuais
                    tk.Label(progress_window, text="Enviando emails...").pack(pady=10)
                    
                    # Cria Treeview para mostrar status dos envios
                    tree = tb.Treeview(progress_window, columns=("Destinatário", "Tipo", "Status"), show="headings", height=5)
                    for col in ("Destinatário", "Tipo", "Status"):
                        tree.heading(col, text=col)
                        tree.column(col, width=120)
                    tree.pack(fill=BOTH, expand=True, padx=10)

                    # Adiciona emails na lista
                    for i, email in enumerate(emails_to_send):
                        tree.insert("", END, iid=str(i), values=(email["recipient"], email["type"], "Pendente"))

                    # Barra de progresso
                    progress = tb.Progressbar(progress_window, maximum=len(emails_to_send), mode='determinate')
                    progress.pack(fill=X, padx=20, pady=10)

                    status_label = tk.Label(progress_window, text="Iniciando envio...")
                    status_label.pack(pady=5)

                    # Função para atualizar interface durante envio
                    def update_progress(success, index, recipient):
                        if not progress_window.winfo_exists():
                            return
                        tree.set(str(index), "Status", "✓ Enviado" if success else "✗ Erro")
                        progress['value'] = index + 1
                        status_label.config(text=f"Enviando para {recipient}...")
                        progress_window.update()

                    # Envia emails
                    success_count = 0
                    for i, email in enumerate(emails_to_send):
                        try:
                            status_label.config(text=f"Enviando para {email['recipient']}...")
                            self.app.email_sender.send_email(
                                recipient=email["recipient"],
                                subject=email["subject"],
                                body=email["body"]
                            )
                            success_count += 1
                            update_progress(True, i, email["recipient"])
                            logger_app.append_log(
                                logger_app.LogLevel.INFO,
                                logger_app.LogCategory.EMAIL,
                                "SYSTEM",
                                "SEND_EMAIL",
                                f"Email enviado com sucesso para {email['recipient']}"
                            )
                        except Exception as e:
                            update_progress(False, i, email["recipient"])
                            logger_app.append_log(
                                logger_app.LogLevel.ERROR,
                                logger_app.LogCategory.EMAIL,
                                "SYSTEM",
                                "SEND_EMAIL_ERROR",
                                f"Erro ao enviar email para {email['recipient']}: {str(e)}"
                            )

                    # Atualiza status final
                    status_text = f"Concluído! {success_count} de {len(emails_to_send)} emails enviados."
                    status_label.config(text=status_text)
                    
                    # Fecha janelas após 3 segundos
                    progress_window.after(3000, lambda: [
                        progress_window.destroy() if progress_window.winfo_exists() else None,
                        addw.destroy() if addw.winfo_exists() else None,
                        refresh_users()
                    ])

                except Exception as e:
                    error_window = tb.Toplevel()
                    error_window.title("Erro")
                    error_window.attributes('-topmost', True)
                    w, h = 400, 150
                    self._center_window(error_window, w, h)
                    self._prevent_resize_maximize(error_window)
                    
                    tb.Label(error_window, text=f"Erro ao cadastrar usuário:\n{str(e)}", 
                            padding=20, wraplength=350).pack()
                    tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()

                    logger_app.append_log(
                        logger_app.LogLevel.ERROR,
                        logger_app.LogCategory.SYSTEM,
                        "SYSTEM",
                        "USER_CREATE_ERROR",
                        f"Erro no cadastro de usuário: {str(e)}"
                    )

            addw = tb.Toplevel(um_window)
            addw.title("Adicionar Usuário")
            w, h = WINDOW_SIZES['add_user']
            self._center_window(addw, w, h)
            self._prevent_resize_maximize(addw)
            addw.attributes('-topmost', True)  # Adiciona sempre no topo

            # Container principal que ocupará toda a janela
            container = tb.Frame(addw)
            container.pack(fill=BOTH, expand=True)

            # Frame com scroll para o conteúdo
            canvas = tb.Canvas(container)
            scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
            
            # Frame que contém o conteúdo scrollável
            content_frame = tb.Frame(canvas)
            content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

            # Configura o scroll
            content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Frame para campos de entrada
            entry_frame = tb.LabelFrame(content_frame, text="Informações do Usuário", padding=15)
            entry_frame.pack(fill=X, expand=True)

            # Configuração do grid
            entry_frame.columnconfigure(0, weight=1, minsize=150)
            entry_frame.columnconfigure(1, weight=3, minsize=350)

            # Variáveis
            login_var = tk.StringVar()
            name_var = tk.StringVar()
            pass_var = tk.StringVar()
            confirm_pass_var = tk.StringVar()
            role_var = tk.StringVar(value="A1")
            email_var = tk.StringVar()
            confirm_email_var = tk.StringVar()

            # Grid para organizar os campos com maior largura
            row = 0
            entry_width = 50  # Aumenta a largura dos campos de entrada

            # Nome completo
            tb.Label(entry_frame, text="Nome completo:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            name_entry = tb.Entry(entry_frame, textvariable=name_var, width=entry_width)
            name_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Login
            tb.Label(entry_frame, text="Login:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            login_entry = tb.Entry(entry_frame, textvariable=login_var, width=entry_width)
            login_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Email
            tb.Label(entry_frame, text="Email:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            email_entry = tb.Entry(entry_frame, textvariable=email_var, width=entry_width)
            email_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Confirmar Email
            tb.Label(entry_frame, text="Confirmar Email:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            confirm_email_entry = tb.Entry(entry_frame, textvariable=confirm_email_var, width=entry_width)
            confirm_email_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Senha
            tb.Label(entry_frame, text="Senha:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            pass_entry = tb.Entry(entry_frame, textvariable=pass_var, show="*", width=entry_width)
            pass_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Confirmar Senha
            tb.Label(entry_frame, text="Confirmar Senha:").grid(row=row, column=0, sticky='w', pady=5, padx=5)
            confirm_pass_entry = tb.Entry(entry_frame, textvariable=confirm_pass_var, show="*", width=entry_width)
            confirm_pass_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=5)
            row += 1

            # Frame para cargos com melhor distribuição
            role_frame = tb.LabelFrame(entry_frame, text="Cargo", padding=10)
            role_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=10, padx=5)

            # Melhor distribuição dos radio buttons
            role_frame.columnconfigure(0, weight=1)
            role_frame.columnconfigure(1, weight=1)
            role_frame.columnconfigure(2, weight=1)

            # Atualizado para mostrar apenas os três cargos
            roles = [
                ("A1", "Visualizador - Apenas visualização de solicitações"),
                ("A3", "Editor - Gerenciamento de solicitações e pagamentos"),
                ("A5", "Administrador - Acesso total ao sistema")
            ]

            for i, (role, desc) in enumerate(roles):
                rb = tb.Radiobutton(
                    role_frame,
                    text=f"{role} - {desc}",
                    variable=role_var,
                    value=role,
                    padding=5
                )
                rb.grid(row=i, column=0, sticky='w', padx=10, pady=5)

            # Frame fixo para botões (fora da área scrollável)
            button_frame = tb.Frame(addw)
            button_frame.pack(side='bottom', fill=X, padx=20, pady=20)

            # Botões centralizados
            tb.Button(
                button_frame,
                text="Adicionar",
                bootstyle=SUCCESS,
                command=confirm_add,
                width=20
            ).pack(side=LEFT, padx=5, expand=True)

            tb.Button(
                button_frame,
                text="Cancelar",
                bootstyle=DANGER,
                command=addw.destroy,
                width=20
            ).pack(side=LEFT, padx=5, expand=True)

            # Configura o canvas e scrollbar
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)

            # Foca no primeiro campo
            name_entry.focus_set()

        def remove_user():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            line = listbox.get(idx)
            user_name = line.split("|")[0].strip()
            if user_name in db_users:
                # Cria janela de confirmação customizada
                confirm_window = tb.Toplevel(um_window)
                confirm_window.title("Confirmar Remoção")
                w, h = 300, 150
                self._center_window(confirm_window, w, h)
                self._prevent_resize_maximize(confirm_window)
                confirm_window.attributes('-topmost', True)  # Adiciona sempre no topo
                
                # Configuração da janela de confirmação
                msg = f"Tem certeza que deseja remover o usuário '{user_name}'?"
                tb.Label(confirm_window, text=msg, wraplength=250).pack(pady=20)
                
                btn_frame = tb.Frame(confirm_window)
                btn_frame.pack(pady=10)
                
                def confirm():
                    db_users.pop(user_name)
                    save_users_db(db_users)
                    refresh_users()
                    confirm_window.destroy()
                
                tb.Button(
                    btn_frame,
                    text="Sim",
                    bootstyle=DANGER,
                    command=confirm
                ).pack(side=LEFT, padx=10)
                
                tb.Button(
                    btn_frame,
                    text="Não",
                    bootstyle=SECONDARY,
                    command=confirm_window.destroy
                ).pack(side=LEFT, padx=10)

        add_btn = tb.Button(btn_frame, text="Adicionar Usuário", bootstyle=SUCCESS, command=add_user)
        add_btn.pack(side=LEFT, padx=5)

        rem_btn = tb.Button(btn_frame, text="Remover Usuário", bootstyle=DANGER, command=remove_user)
        rem_btn.pack(side=LEFT, padx=5)

    def setup_notification_cargos(self):
        notif_window = tb.Toplevel(self.app.root)
        notif_window.title("Configurar Emails de Notificação")
        w, h = WINDOW_SIZES['notification']
        self._center_window(notif_window, w, h)
        self._prevent_resize_maximize(notif_window)
        notif_window.attributes('-topmost', True)  # Adiciona sempre no topo

        notebook = tb.Notebook(notif_window)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Dicionário com títulos mais amigáveis para as abas
        tab_titles = {
            "AguardandoAprovacao": "Recebimento de solicitação",
            "Solicitação Aceita": "Solicitação aceita",
            "ProntoPagamento": "Pronto para Pagamento",
            "Cancelado": "Cancelados",
            "ADMIN": "Administradores"  # Nova aba para emails admin
        }

        notification_emails = self.app.sheets_handler.get_notification_emails()
        tabs = {}

        for event_type, title in tab_titles.items():
            tab = tb.Frame(notebook, padding=10)
            notebook.add(tab, text=title)
            
            # Frame para lista e botões
            list_frame = tb.Frame(tab)
            list_frame.pack(fill=BOTH, expand=True)
            
            # Listbox com scrollbar
            listbox = tk.Listbox(list_frame, height=15)
            scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            
            listbox.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # Preencher listbox com emails existentes
            for email in notification_emails.get(event_type, []):
                if email.strip():
                    listbox.insert(END, email.strip())
            
            # Frame para botões
            btn_frame = tb.Frame(tab)
            btn_frame.pack(fill=X, pady=10)
            
            def add_email(lb=listbox, et=event_type):
                dialog = tb.Toplevel(notif_window)
                dialog.title("Adicionar Email")
                w, h = WINDOW_SIZES['add_email']
                self._center_window(dialog, w, h)
                self._prevent_resize_maximize(dialog)

                tk.Label(dialog, text="Email:").pack(pady=5)
                email_var = tk.StringVar()
                entry = tk.Entry(dialog, textvariable=email_var, width=40)
                entry.pack(pady=5)

                def save():
                    email = email_var.get().strip()
                    if email:
                        lb.insert(END, email)
                        # Atualizar na planilha
                        emails = list(lb.get(0, END))
                        self.app.sheets_handler.update_notification_emails(et, emails)
                    dialog.destroy()

                tb.Button(dialog, text="Adicionar", bootstyle=SUCCESS, command=save).pack(pady=10)

            def remove_email(lb=listbox, et=event_type):
                selection = lb.curselection()
                if selection:
                    lb.delete(selection)
                    # Atualizar na planilha
                    emails = list(lb.get(0, END))
                    self.app.sheets_handler.update_notification_emails(et, emails)

            tb.Button(btn_frame, text="Adicionar Email", bootstyle=SUCCESS, 
                     command=lambda l=listbox, e=event_type: add_email(l, e)).pack(side=LEFT, padx=5)
            tb.Button(btn_frame, text="Remover Email", bootstyle=DANGER, 
                     command=lambda l=listbox, e=event_type: remove_email(l, e)).pack(side=LEFT, padx=5)

            tabs[event_type] = tab

        # Botão de fechar
        tb.Button(notif_window, text="Fechar", bootstyle=PRIMARY, 
                 command=notif_window.destroy).pack(pady=10)

    def show_logs(self):
        """Abre o visualizador de logs"""
        from app.log_viewer import LogViewer
        LogViewer(self.app.root)

    def manage_machines(self):
        """Interface para gerenciamento de máquinas autorizadas"""
        
        mm_window = tb.Toplevel(self.app.root)
        mm_window.title("Gerenciar Máquinas")
        w, h = WINDOW_SIZES['machine_manager']
        self._center_window(mm_window, w, h)
        self._prevent_resize_maximize(mm_window)
        mm_window.attributes('-topmost', True)

        # Frame principal
        main_frame = tb.Frame(mm_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame superior para título
        title_frame = tb.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0,10))
        
        title = tb.Label(
            title_frame, 
            text="Lista de Máquinas Autorizadas",
            font=("Helvetica", 12, "bold")
        )
        title.pack(pady=5)

        # Frame para lista de máquinas
        list_frame = tb.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)

        # Treeview para listar máquinas
        columns = ("Hostname", "IP", "Data Registro")
        tree = tb.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Hostname":
                tree.column(col, width=200)
            elif col == "IP":
                tree.column(col, width=150)
            else:
                tree.column(col, width=150)

        tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Frame para botões
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        def refresh_list():
            machine_manager = MachineManager("credentials.json")
            for i in tree.get_children():
                tree.delete(i)
            machines = machine_manager.get_registered_machines()
            for machine in machines:
                # Pega apenas hostname, IP e data
                hostname = machine[2]
                ip = machine[3]
                date = machine[4]
                tree.insert("", "end", values=(hostname, ip, date))

        def register_current():
            machine_manager = MachineManager("credentials.json")
            if machine_manager.register_machine():
                msg_window = tb.Toplevel()
                msg_window.title("Sucesso")
                msg_window.attributes('-topmost', True)  # Garante sempre visível
                self._center_window(msg_window, 300, 100)
                self._prevent_resize_maximize(msg_window)
                
                tb.Label(msg_window, text="Máquina registrada com sucesso!", padding=20).pack()
                tb.Button(msg_window, text="OK", command=msg_window.destroy, width=10).pack()
                
                refresh_list()
            else:
                error_window = tb.Toplevel()
                error_window.title("Erro")
                error_window.attributes('-topmost', True)  # Garante sempre visível
                self._center_window(error_window, 300, 100)
                self._prevent_resize_maximize(error_window)
                
                tb.Label(error_window, text="Falha ao registrar máquina", padding=20).pack()
                tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()

        def remove_selected():
            selected = tree.selection()
            if not selected:
                warn_window = tb.Toplevel()
                warn_window.title("Aviso")
                warn_window.attributes('-topmost', True)  # Garante sempre visível
                self._center_window(warn_window, 300, 100)
                self._prevent_resize_maximize(warn_window)
                
                tb.Label(warn_window, text="Selecione uma máquina para remover", padding=20).pack()
                tb.Button(warn_window, text="OK", command=warn_window.destroy, width=10).pack()
                return
                
            # Janela de confirmação
            confirm_window = tb.Toplevel()
            confirm_window.title("Confirmar")
            confirm_window.attributes('-topmost', True)  # Garante sempre visível
            self._center_window(confirm_window, 300, 150)
            self._prevent_resize_maximize(confirm_window)
            
            tb.Label(confirm_window, text="Deseja remover a máquina selecionada?", padding=20).pack()
            
            def confirm_remove():
                confirm_window.destroy()
                idx = tree.index(selected[0]) + 2
                machine_manager = MachineManager("credentials.json")
                if machine_manager.remove_machine(idx):
                    success_window = tb.Toplevel()
                    success_window.title("Sucesso")
                    success_window.attributes('-topmost', True)
                    self._center_window(success_window, 300, 100)
                    self._prevent_resize_maximize(success_window)
                    
                    tb.Label(success_window, text="Máquina removida com sucesso!", padding=20).pack()
                    tb.Button(success_window, text="OK", command=success_window.destroy, width=10).pack()
                    
                    refresh_list()
                else:
                    error_window = tb.Toplevel()
                    error_window.title("Erro")
                    error_window.attributes('-topmost', True)
                    self._center_window(error_window, 300, 100)
                    self._prevent_resize_maximize(error_window)
                    
                    tb.Label(error_window, text="Falha ao remover máquina", padding=20).pack()
                    tb.Button(error_window, text="OK", command=error_window.destroy, width=10).pack()
        
            btn_frame = tb.Frame(confirm_window)
            btn_frame.pack(pady=10)
            
            tb.Button(btn_frame, text="Sim", bootstyle=DANGER, command=confirm_remove).pack(side=LEFT, padx=10)
            tb.Button(btn_frame, text="Não", bootstyle=SECONDARY, command=confirm_window.destroy).pack(side=LEFT, padx=10)

        # Botões com novo estilo e tamanho
        btn_register = tb.Button(
            btn_frame,
            text="Registrar Esta Máquina",
            bootstyle=SUCCESS,
            width=25,
            command=register_current
        )
        btn_register.pack(side="left", padx=5)

        btn_remove = tb.Button(
            btn_frame,
            text="Remover Selecionada",
            bootstyle=DANGER,
            width=25,
            command=remove_selected
        )
        btn_remove.pack(side="left", padx=5)

        btn_refresh = tb.Button(
            btn_frame,
            text="Atualizar Lista",
            bootstyle=INFO,
            width=25,
            command=refresh_list
        )
        btn_refresh.pack(side="left", padx=5)

        # Carrega lista inicial
        refresh_list()
