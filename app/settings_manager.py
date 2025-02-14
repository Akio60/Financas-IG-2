# settings_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import json
import os
import hashlib

BTN_WIDTH = 35

USERS_DB_FILE = "users_db.json"

# Tamanhos padrão de janelas
WINDOW_SIZES = {
    'settings': (600, 480),  # Janela principal de configurações
    'column_selector': (600, 480),  # Seletor de colunas
    'user_manager': (600, 480),  # Gerenciador de usuários
    'add_user': (400, 480),  # Adicionar usuário
    'email_template': (600, 480),  # Editor de template de email
    'notification': (600, 480),  # Configuração de notificações
    'add_email': (400, 150),  # Adicionar email dialog
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
    ROLE_NAMES = {
        "A1": "Visualizador",
        "A2": "Editor Básico",
        "A3": "Editor Avançado",
        "A4": "Financeiro",
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
            
        row_start_col = 5
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
                text=f"Template: {template_name}", 
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
            addw = tb.Toplevel(um_window)
            addw.title("Adicionar Usuário")
            w, h = WINDOW_SIZES['add_user']
            self._center_window(addw, w, h)
            self._prevent_resize_maximize(addw)

            tk.Label(addw, text="Login:").pack(pady=5)
            login_var = tk.StringVar()
            login_entry = tk.Entry(addw, textvariable=login_var)
            login_entry.pack()

            tk.Label(addw, text="Senha:").pack(pady=5)
            pass_var = tk.StringVar()
            pass_entry = tk.Entry(addw, textvariable=pass_var, show="*")
            pass_entry.pack()

            tk.Label(addw, text="Confirmar Senha:").pack(pady=5)
            confirm_pass_var = tk.StringVar()
            confirm_pass_entry = tk.Entry(addw, textvariable=confirm_pass_var, show="*")
            confirm_pass_entry.pack()

            tk.Label(addw, text="Cargo:").pack(pady=5)
            role_var = tk.StringVar(value="A1")
            role_frame = tk.Frame(addw)
            role_frame.pack(pady=5)

            for role, name in self.ROLE_NAMES.items():
                rb = tk.Radiobutton(role_frame, text=f"{role} - {name}", 
                                  variable=role_var, value=role)
                rb.pack(anchor='w')

            tk.Label(addw, text="Email:").pack(pady=5)
            email_var = tk.StringVar()
            email_entry = tk.Entry(addw, textvariable=email_var)
            email_entry.pack()

            def confirm_add():
                user = login_var.get().strip()
                pwd = pass_var.get().strip()
                confirm_pwd = confirm_pass_var.get().strip()
                r = role_var.get().strip()
                em = email_var.get().strip()

                if not user or not pwd or not r or not em:
                    messagebox.showwarning("Aviso", "Preencha todos os campos!")
                    return
                if pwd != confirm_pwd:
                    messagebox.showwarning("Aviso", "As senhas não coincidem!")
                    return
                if user in db_users:
                    messagebox.showwarning("Aviso", "Usuário já existe.")
                    return

                hashed_pwd = hash_password(pwd+user)
                db_users[user] = {
                    "hashed_password": hashed_pwd, 
                    "role": r, 
                    "email": em,
                    "role_name": self.ROLE_NAMES[r]
                }
                save_users_db(db_users)
                refresh_users()
                addw.destroy()

            tb.Button(addw, text="Adicionar", bootstyle=SUCCESS, command=confirm_add).pack(pady=10)

        def remove_user():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            line = listbox.get(idx)
            user_name = line.split("|")[0].strip()
            if user_name in db_users:
                confirm = messagebox.askyesno("Confirmar", f"Remover usuário '{user_name}'?")
                if confirm:
                    db_users.pop(user_name)
                    save_users_db(db_users)
                    refresh_users()

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

        notebook = tb.Notebook(notif_window)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Dicionário com títulos mais amigáveis para as abas
        tab_titles = {
            "AguardandoAprovacao": "Recebimento de solicitação",
            "Solicitação Aceita": "Solicitação aceita",
            "ProntoPagamento": "Pronto para Pagamento",
            "Cancelado": "Cancelados",
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
