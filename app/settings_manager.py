# settings_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Text, messagebox

class SettingsManager:
    def __init__(self, app):
        self.app = app

    def open_settings(self):
        """
        Abre janela de configurações com layout de 2 colunas,
        remove a edição de cores de status,
        mantém seleção de tema, seleção de colunas (com reorder) e edição de e-mails.
        """
        settings_window = tb.Toplevel(self.app.root)
        settings_window.title("Configurações")
        settings_window.geometry("700x400")

        # Frame principal (grid com 2 colunas)
        main_frame = tb.Frame(settings_window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        # -------------- COLUNA 1 --------------
        col1 = tb.Frame(main_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        col1.columnconfigure(0, weight=1)

        instructions_label = tb.Label(
            col1,
            text="Configurações de Interface e Colunas",
            font=("Helvetica", 12, "bold")
        )
        instructions_label.grid(row=0, column=0, sticky='w', pady=5)

        theme_label = tb.Label(
            col1,
            text="Selecione um tema:",
            font=("Helvetica", 10, "bold")
        )
        theme_label.grid(row=1, column=0, sticky='w', pady=5)

        # 5 temas fixos
        themes_list = ["flatly", "darkly", "cyborg", "superhero", "cosmo"]
        theme_combo = tb.Combobox(col1, values=themes_list, state='readonly', width=25)
        theme_combo.grid(row=2, column=0, sticky='w', pady=5)

        def change_theme(event):
            selected_theme = theme_combo.get()
            # Se a raiz suportar set_theme (ttkbootstrap.Window), usamos:
            if hasattr(self.app.root, 'set_theme'):
                self.app.root.set_theme(selected_theme)
            else:
                messagebox.showinfo("Aviso", "Não é possível mudar o tema (set_theme indisponível).")

        theme_combo.bind('<<ComboboxSelected>>', change_theme)

        columns_label = tb.Label(
            col1,
            text="Colunas por Visualização:",
            font=("Helvetica", 10, "bold")
        )
        columns_label.grid(row=3, column=0, sticky='w', pady=(15, 5))

        button_style = {"bootstyle": INFO, "width":25}  # define estilo e largura p/ uniformizar

        views = [
            ("Aguardando aprovação", "Aguardando aprovação"),
            ("Pendências", "Pendências"),
            ("Pronto para pagamento", "Pronto para pagamento")
        ]

        row_index = 4
        for label_text, view_name in views:
            btn = tb.Button(
                col1,
                text=f"Editar colunas: {label_text}",
                command=lambda v=view_name: self.open_column_selector(v),
                **button_style
            )
            btn.grid(row=row_index, column=0, sticky='w', pady=5)
            row_index += 1

        # -------------- COLUNA 2 --------------
        col2 = tb.Frame(main_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        col2.columnconfigure(0, weight=1)

        email_section_label = tb.Label(
            col2,
            text="Editar Modelos de E-mail:",
            font=("Helvetica", 12, "bold")
        )
        email_section_label.grid(row=0, column=0, sticky='w', pady=5)

        infobox_text = (
            "Use chaves {} para inserir dados do formulário.\n"
            "Ex.: {Nome}, {CPF:}, {Telefone de contato:}, etc.\n"
            "Esses campos serão substituídos dinamicamente."
        )
        infobox_label = tb.Label(
            col2,
            text=infobox_text,
            font=("Helvetica", 9),
            foreground="gray"
        )
        infobox_label.grid(row=1, column=0, sticky='w', pady=5)

        row_index2 = 2
        for motivo in self.app.email_templates.keys():
            button = tb.Button(
                col2,
                text=f"Editar E-mail para {motivo}",
                bootstyle=SECONDARY,
                width=25,
                command=lambda m=motivo: self.edit_email_template(m)
            )
            button.grid(row=row_index2, column=0, sticky='w', pady=5)
            row_index2 += 1

        col2.rowconfigure(row_index2, weight=1)
        col1.rowconfigure(row_index, weight=1)

    def open_column_selector(self, view_name):
        """
        Abre uma janela que permite selecionar e reordenar colunas para a 'view_name'.
        """
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Configurar Colunas - {view_name}")
        sel_window.geometry("600x400")

        label = tb.Label(sel_window, text=f"Selecione/Reordene colunas para '{view_name}':",
                         font=("Helvetica", 11, "bold"))
        label.pack(pady=10)

        # Colunas possíveis
        all_possible_columns = [
            'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
            'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
            'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
            'Telefone de contato:', 'Carimbo de data/hora_str', 'Status', 'Ultima Atualizacao', 'Valor',
            'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
            'RG/RNE:', 'Dados bancários (banco, agência e conta) '
        ]

        current_cols = self.app.custom_views.get(view_name, [])

        # Frame para Checkbuttons + Listbox
        top_frame = tb.Frame(sel_window)
        top_frame.pack(fill=BOTH, expand=True)

        # Checkbuttons (coluna da esquerda)
        left_frame = tb.Frame(top_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)

        tk_label_available = tb.Label(left_frame, text="Colunas Disponíveis")
        tk_label_available.pack(anchor='w')

        # Dicionário booleano p/ check
        var_dict = {}
        for col in all_possible_columns:
            var_dict[col] = tb.BooleanVar(value=(col in current_cols))

        def on_cb_click(c):
            if var_dict[c].get():
                if c not in current_cols:
                    current_cols.append(c)
            else:
                if c in current_cols:
                    current_cols.remove(c)
            refresh_listbox()

        for col in all_possible_columns:
            cb = tb.Checkbutton(
                left_frame,
                text=col,
                variable=var_dict[col],
                command=lambda c=col: on_cb_click(c)
            )
            cb.pack(anchor='w')

        # Listbox (coluna da direita) para reordenar
        right_frame = tb.Frame(top_frame)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        tk_label_order = tb.Label(right_frame, text="Ordem das Colunas Selecionadas")
        tk_label_order.pack(anchor='w')

        listbox = tb.Listbox(right_frame, height=15)
        listbox.pack(fill=BOTH, expand=True)

        def refresh_listbox():
            listbox.delete(0, 'end')
            for col in current_cols:
                listbox.insert('end', col)

        def move_up():
            sel = listbox.curselection()
            if not sel:
                return
            index = sel[0]
            if index == 0:
                return
            # Swap
            current_cols[index], current_cols[index-1] = current_cols[index-1], current_cols[index]
            refresh_listbox()
            listbox.selection_set(index-1)

        def move_down():
            sel = listbox.curselection()
            if not sel:
                return
            index = sel[0]
            if index == len(current_cols) - 1:
                return
            current_cols[index], current_cols[index+1] = current_cols[index+1], current_cols[index]
            refresh_listbox()
            listbox.selection_set(index+1)

        btn_frame = tb.Frame(right_frame)
        btn_frame.pack(pady=5)

        up_btn = tb.Button(btn_frame, text="Mover Para Cima", bootstyle=INFO, command=move_up)
        up_btn.grid(row=0, column=0, padx=5)

        down_btn = tb.Button(btn_frame, text="Mover Para Baixo", bootstyle=INFO, command=move_down)
        down_btn.grid(row=0, column=1, padx=5)

        refresh_listbox()

        def close_and_save():
            self.app.custom_views[view_name] = current_cols
            sel_window.destroy()

        close_btn = tb.Button(sel_window, text="Salvar e Fechar", bootstyle=SUCCESS, command=close_and_save)
        close_btn.pack(pady=10)

    def edit_email_template(self, motivo):
        """
        Abre janela para editar o template de e-mail referente ao 'motivo'.
        """
        template_window = tb.Toplevel(self.app.root)
        template_window.title(f"Editar Modelo de E-mail para {motivo}")
        template_window.geometry("600x400")

        label = tb.Label(
            template_window,
            text=f"Editando o modelo de e-mail para {motivo}:",
            font=("Helvetica", 12)
        )
        label.pack(pady=10)

        text_widget = tb.ScrolledText(template_window, width=70, height=15)
        text_widget.pack(pady=10, padx=10)
        text_widget.insert('1.0', self.app.email_templates[motivo])

        def save_template():
            new_template = text_widget.get("1.0", 'end').strip()
            self.app.email_templates[motivo] = new_template
            self.app.save_email_templates()
            template_window.destroy()

        save_button = tb.Button(template_window, text="Salvar", bootstyle=SUCCESS, command=save_template)
        save_button.pack(pady=10)
