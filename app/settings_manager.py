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
        mantém seleção de tema, seleção de colunas e edição de e-mails.
        """
        settings_window = tb.Toplevel(self.app.root)
        settings_window.title("Configurações")
        settings_window.geometry("700x400")

        # Frame principal (grid com 2 colunas)
        main_frame = tb.Frame(settings_window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # =============== COLUNA 1 ===============
        col1 = tb.Frame(main_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        col1.columnconfigure(0, weight=1)

        # Título
        instructions_label = tb.Label(
            col1,
            text="Configurações de Interface e Colunas",
            font=("Helvetica", 12, "bold")
        )
        instructions_label.grid(row=0, column=0, sticky='w', pady=5)

        # SEÇÃO: TEMA
        theme_label = tb.Label(
            col1,
            text="Selecione um tema (ttkbootstrap):",
            font=("Helvetica", 10, "bold")
        )
        theme_label.grid(row=1, column=0, sticky='w', pady=5)

        # 5 temas fixos
        themes_list = ["flatly", "darkly", "cyborg", "superhero", "cosmo"]
        theme_combo = tb.Combobox(col1, values=themes_list, state='readonly')
        theme_combo.grid(row=2, column=0, sticky='w', pady=5)

        def change_theme(event):
            selected_theme = theme_combo.get()
            self.app.root.set_theme(selected_theme)

        theme_combo.bind('<<ComboboxSelected>>', change_theme)

        # SEÇÃO: BOTÕES PARA SELECIONAR COLUNAS
        columns_label = tb.Label(
            col1,
            text="Colunas por Visualização:",
            font=("Helvetica", 10, "bold")
        )
        columns_label.grid(row=3, column=0, sticky='w', pady=(15, 5))

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
                bootstyle=INFO,
                command=lambda v=view_name: self.open_column_selector(v)
            )
            btn.grid(row=row_index, column=0, sticky='w', pady=5)
            row_index += 1

        # Ajusta col1 para crescer verticalmente
        col1.rowconfigure(row_index, weight=1)

        # =============== COLUNA 2 ===============
        col2 = tb.Frame(main_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        col2.columnconfigure(0, weight=1)

        # SEÇÃO: EDIÇÃO DE EMAILS
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
                command=lambda m=motivo: self.edit_email_template(m)
            )
            button.grid(row=row_index2, column=0, sticky='w', pady=5)
            row_index2 += 1

        # Ajusta col2 para crescer
        col2.rowconfigure(row_index2, weight=1)

        # =============== AJUSTE DE GRID ===============
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def open_column_selector(self, view_name):
        """
        Abre uma janela que permite selecionar quais colunas serão exibidas
        para a 'view_name' especificada.
        """
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Configurar Colunas - {view_name}")
        sel_window.geometry("500x400")

        label = tb.Label(sel_window, text=f"Selecione as colunas para '{view_name}':", font=("Helvetica", 11, "bold"))
        label.pack(pady=10)

        # Colunas possíveis (você pode ajustar conforme seu uso real)
        all_possible_columns = [
            'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
            'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
            'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
            'Telefone de contato:', 'Carimbo de data/hora_str', 'Status', 'Ultima Atualizacao', 'Valor',
            'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
            'RG/RNE:', 'Dados bancários (banco, agência e conta) '
        ]

        current_cols = self.app.custom_views.get(view_name, [])

        var_dict = {}
        for col in all_possible_columns:
            var = tb.BooleanVar(value=(col in current_cols))
            var_dict[col] = var

            def toggle_col(c=col):
                if var_dict[c].get():
                    if c not in current_cols:
                        current_cols.append(c)
                else:
                    if c in current_cols:
                        current_cols.remove(c)

            cb = tb.Checkbutton(
                sel_window,
                text=col,
                variable=var,
                command=toggle_col
            )
            cb.pack(anchor='w')

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
