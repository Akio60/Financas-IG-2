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
NOTIFICATION_CARGOS_FILE = "notification_cargos.json"
TABLE_COLORS_FILE = "table_colors.json"

def load_users_db():
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users_db(db):
    with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def load_notification_cargos():
    if os.path.exists(NOTIFICATION_CARGOS_FILE):
        with open(NOTIFICATION_CARGOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "AguardandoAprovacao": "A2",
        "Pendencias": "A3",
        "ProntoPagamento": "A4",
        "Cancelado": "A1",
        "Autorizado": "A3"
    }

def save_notification_cargos(cfg):
    with open(NOTIFICATION_CARGOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

def load_table_colors():
    if os.path.exists(TABLE_COLORS_FILE):
        with open(TABLE_COLORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "background": "#ffffff",
        "foreground": "#000000",
        "oddrow": "#f0f8ff",
        "evenrow": "#ffffff",
        "selected": "#d3d3d3"
    }

def save_table_colors(colors):
    with open(TABLE_COLORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(colors, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """Retorna o hash SHA-256 da senha fornecida."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class SettingsManager:
    def __init__(self, app):
        self.app = app
        self.settings_window = None
        self.mask_window = None

        self.users_db = load_users_db()
        self.notification_cargos = load_notification_cargos()

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tb.Toplevel(self.app.root)
        self.settings_window.title("Configurações")
        self.settings_window.geometry("800x500")

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
            
            mask_btn = tb.Button(
                col1,
                text="Títulos de Informações",
                bootstyle=WARNING,
                width=BTN_WIDTH,
                command=self.open_mask_editor
            )
            mask_btn.grid(row=1, column=0, sticky='w', pady=10)
            
            user_btn = tb.Button(
                col1,
                text="Cadastrar/Remover Usuários",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.user_management
            )
            user_btn.grid(row=2, column=0, sticky='w', pady=10)

            notif_btn = tb.Button(
                col1,
                text="Configurar cargo de notificação",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.setup_notification_cargos
            )
            notif_btn.grid(row=3, column=0, sticky='w', pady=10)
            
            color_btn = tb.Button(
                col1,
                text="Gerir Cores das Tabelas",
                bootstyle=INFO,
                width=BTN_WIDTH,
                command=self.manage_table_colors
            )
            color_btn.grid(row=4, column=0, sticky='w', pady=10)

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
            ("Aguardando aprovação", "Aguardando aprovação"),
            ("Aceitas", "Aceitas"),
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

    def manage_table_colors(self):
        colors = load_table_colors()
        color_win = tb.Toplevel(self.app.root)
        color_win.title("Gerenciar Cores das Tabelas")
        color_win.geometry("400x300")

        lbl = tb.Label(color_win, text="Defina as cores para a exibição das tabelas:", font=("Helvetica", 10, "bold"))
        lbl.pack(pady=10)

        frame = tb.Frame(color_win)
        frame.pack(pady=10)

        entries = {}
        for i, key in enumerate(["background", "foreground", "oddrow", "evenrow", "selected"]):
            tk.Label(frame, text=key.capitalize() + ":").grid(row=i, column=0, sticky='e', padx=5, pady=5)
            var = tk.StringVar(value=colors.get(key, ""))
            entry = tk.Entry(frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = var

        def save_colors():
            new_colors = {key: var.get().strip() for key, var in entries.items()}
            save_table_colors(new_colors)
            messagebox.showinfo("Sucesso", "Cores atualizadas. Reinicie o aplicativo para ver as mudanças.")
            color_win.destroy()

        save_btn = tb.Button(color_win, text="Salvar Cores", bootstyle=SUCCESS, width=BTN_WIDTH, command=save_colors)
        save_btn.pack(pady=10)

    def open_column_selector(self, view_name):
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Colunas - {view_name}")
        sel_window.geometry("700x400")

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

    def open_mask_editor(self):
        if self.mask_window and self.mask_window.winfo_exists():
            self.mask_window.lift()
            return

        self.mask_window = tb.Toplevel(self.app.root)
        self.mask_window.title("Editar Títulos de Informações")
        self.mask_window.geometry("600x500")

        info_label = tb.Label(
            self.mask_window,
            text="Edite os nomes/títulos exibidos ao usuário, sem alterar as chaves internas.",
            font=("Helvetica", 9),
            foreground="gray",
            wraplength=550
        )
        info_label.pack(pady=5, padx=5)

        frame_scroll = tb.Frame(self.mask_window)
        frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_scroll)
        scrollbar = tb.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0,0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.entry_vars = {}
        field_map = self.app.details_manager.FORM_FIELD_MAPPING

        row_idx = 0
        for key, val in field_map.items():
            tk_label = tb.Label(scroll_frame, text=key, width=40, anchor='w')
            tk_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky='w')
            var = tk.StringVar(value=val)
            self.entry_vars[key] = var
            tk_entry = tk.Entry(scroll_frame, textvariable=var, width=40)
            tk_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky='w')
            row_idx += 1

        def save_masks():
            for k, v in self.entry_vars.items():
                field_map[k] = v.get().strip()
            messagebox.showinfo("Sucesso", "Títulos atualizados.")
            self.mask_window.destroy()

        save_btn = tb.Button(self.mask_window, text="Salvar Títulos", bootstyle=SUCCESS, width=BTN_WIDTH, command=save_masks)
        save_btn.pack(pady=5)

    def edit_email_template(self, motivo):
        template_window = tb.Toplevel(self.app.root)
        template_window.title(motivo)
        template_window.geometry("600x400")

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
        um_window.geometry("500x400")

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
            addw.geometry("300x250")

            tk.Label(addw, text="Login:").pack(pady=5)
            login_var = tk.StringVar()
            login_entry = tk.Entry(addw, textvariable=login_var)
            login_entry.pack()

            tk.Label(addw, text="Senha:").pack(pady=5)
            pass_var = tk.StringVar()
            pass_entry = tk.Entry(addw, textvariable=pass_var)
            pass_entry.pack()

            tk.Label(addw, text="Cargo (A1..A5):").pack(pady=5)
            role_var = tk.StringVar(value="A1")
            role_entry = tk.Entry(addw, textvariable=role_var)
            role_entry.pack()

            tk.Label(addw, text="Email:").pack(pady=5)
            email_var = tk.StringVar()
            email_entry = tk.Entry(addw, textvariable=email_var)
            email_entry.pack()

            def confirm_add():
                user = login_var.get().strip()
                pwd = pass_var.get().strip()
                r = role_var.get().strip()
                em = email_var.get().strip()
                if not user or not pwd or not r or not em:
                    messagebox.showwarning("Aviso", "Preencha todos os campos!")
                    return
                if user in db_users:
                    messagebox.showwarning("Aviso", "Usuário já existe.")
                    return
                # Cria o hash da senha usando a função hash_password
                hashed_pwd = hash_password(pwd+user)
                db_users[user] = {"hashed_password": hashed_pwd, "role": r, "email": em}
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
        notif_window.geometry("600x500")

        notification_emails = self.app.sheets_handler.get_notification_emails()

        # Frame principal com scroll
        main_frame = tb.Frame(notif_window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Criar frames para cada tipo de notificação
        for event_type in ["AguardandoAprovacao", "Pendencias", "ProntoPagamento", "Cancelado", "Autorizado"]:
            frame = tb.LabelFrame(main_frame, text=event_type, padding=10)
            frame.pack(fill=X, pady=5)

            # Listbox para emails
            listbox = tk.Listbox(frame, height=4)
            listbox.pack(side=LEFT, fill=BOTH, expand=True)
            
            # Preencher listbox com emails existentes
            for email in notification_emails.get(event_type, []):
                if email.strip():
                    listbox.insert(END, email.strip())

            # Frame para botões
            btn_frame = tb.Frame(frame)
            btn_frame.pack(side=RIGHT, fill=Y, padx=5)

            def add_email(lb=listbox, et=event_type):
                dialog = tb.Toplevel(notif_window)
                dialog.title("Adicionar Email")
                dialog.geometry("300x150")

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

            tb.Button(btn_frame, text="Adicionar", bootstyle=SUCCESS, 
                     command=lambda l=listbox, e=event_type: add_email(l, e)).pack(pady=2)
            tb.Button(btn_frame, text="Remover", bootstyle=DANGER, 
                     command=lambda l=listbox, e=event_type: remove_email(l, e)).pack(pady=2)

        # Botão de fechar
        tb.Button(notif_window, text="Fechar", bootstyle=PRIMARY, 
                 command=notif_window.destroy).pack(pady=10)
