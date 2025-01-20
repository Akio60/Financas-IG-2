# settings_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Text, messagebox, colorchooser
#from .column_selector import ColumnSelector  # (EXTRA) Se quisermos separar a lógica

class SettingsManager:
    def __init__(self, app):
        self.app = app

    def open_settings(self):
        """
        Abre janela de configurações com:
         - Seleção de tema
         - Botão para editar cores de status
         - Botões para selecionar colunas de cada visualização
         - Botões para editar templates de e-mail
         - Infobox explicando formatação
        """
        settings_window = tb.Toplevel(self.app.root)
        settings_window.title("Configurações")
        settings_window.geometry("700x650")

        instructions = (
            "Nesta seção, você pode editar os modelos de e-mail utilizados.\n"
            "Use chaves para inserir dados do formulário. Ex.: {Nome}, {Curso}, etc.\n\n"
            "Também é possível alterar o tema da interface e configurar as cores dos status.\n"
            "Ao clicar em cada botão de colunas, você poderá escolher quais colunas aparecem em cada visualização."
        )
        instructions_label = tb.Label(
            settings_window,
            text=instructions,
            font=("Helvetica", 10),
            justify='left'
        )
        instructions_label.pack(pady=5, padx=10)

        # -------------------------------
        # Seção para MUDAR O TEMA
        # -------------------------------
        theme_label = tb.Label(
            settings_window,
            text="Selecione um tema:",
            font=("Helvetica", 11, "bold")
        )
        theme_label.pack(pady=5, padx=10, anchor='w')

        themes_list = ["flatly", "darkly", "cyborg", "superhero", "cosmo"]
        theme_combo = tb.Combobox(settings_window, values=themes_list, state='readonly')
        theme_combo.pack(pady=5, padx=10, fill=X)

        def change_theme(event):
            selected_theme = theme_combo.get()
            self.app.root.set_theme(selected_theme)

        theme_combo.bind('<<ComboboxSelected>>', change_theme)

        # -------------------------------
        # Botão para EDITAR CORES de cada STATUS
        # -------------------------------
        color_edit_button = tb.Button(
            settings_window,
            text="Editar cores de Status",
            bootstyle=WARNING,
            command=self.edit_status_colors
        )
        color_edit_button.pack(pady=10, padx=10, fill=X)

        # -------------------------------
        # Botões para SELECIONAR COLUNAS
        # -------------------------------
        columns_label = tb.Label(
            settings_window,
            text="Configurar colunas a exibir em cada visualização:",
            font=("Helvetica", 11, "bold")
        )
        columns_label.pack(pady=5, padx=10, anchor='w')

        # Três botões, um para cada visualização
        views = [
            ("Aguardando aprovação", "Aguardando aprovação"),
            ("Pendências", "Pendências"),
            ("Pronto para pagamento", "Pronto para pagamento")
        ]

        for label_text, view_name in views:
            btn = tb.Button(
                settings_window,
                text=f"Editar colunas: {label_text}",
                bootstyle=INFO,
                command=lambda v=view_name: self.open_column_selector(v)
            )
            btn.pack(pady=5, padx=20, fill=X)

        # -------------------------------
        # SEÇÃO de EDICÃO de E-MAIL
        # -------------------------------
        email_section_label = tb.Label(
            settings_window,
            text="Editar Modelos de E-mail:",
            font=("Helvetica", 11, "bold")
        )
        email_section_label.pack(pady=(20, 5), padx=10, anchor='w')

        # Infobox discreto explicando formatação
        infobox_text = (
            "Utilize chaves {} para inserir dados do formulário.\n"
            "Ex.: {Nome}, {CPF:}, {Telefone de contato:}, etc.\n"
            "Esses campos serão substituídos dinamicamente."
        )
        infobox_label = tb.Label(
            settings_window,
            text=infobox_text,
            font=("Helvetica", 9),
            foreground="gray"
        )
        infobox_label.pack(pady=5, padx=10, anchor='w')

        # Botões para cada motivo
        for motivo in self.app.email_templates.keys():
            button = tb.Button(
                settings_window,
                text=f"Editar E-mail para {motivo}",
                bootstyle=SECONDARY,
                command=lambda m=motivo: self.edit_email_template(m)
            )
            button.pack(pady=5, padx=10, fill=X)

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

    # -----------------------------------------
    # 1) MÉTODO PARA EDITAR CORES DE STATUS
    # -----------------------------------------
    def edit_status_colors(self):
        """
        Abre uma janela permitindo escolher cores para cada status do dicionário self.app.status_colors.
        """
        color_window = tb.Toplevel(self.app.root)
        color_window.title("Editar Cores dos Status")
        color_window.geometry("400x300")

        label = tb.Label(color_window, text="Selecione a cor para cada Status", font=("Helvetica", 11, "bold"))
        label.pack(pady=10)

        # Para cada status no dict, criar um botão que abre colorchooser
        for status, current_color in self.app.status_colors.items():
            frame = tb.Frame(color_window)
            frame.pack(fill=X, padx=10, pady=5)

            status_label = tb.Label(frame, text=status, width=25)
            status_label.pack(side=LEFT)

            def choose_color(s=status):
                # Abre color chooser
                c = colorchooser.askcolor(color=self.app.status_colors[s], title=f"Cor para {s}")
                if c and c[1] is not None:  # c[1] é a string em formato #RRGGBB
                    self.app.status_colors[s] = c[1]  # atualiza dicionário

            color_btn = tb.Button(frame, text=current_color, bootstyle=INFO, command=choose_color)
            color_btn.pack(side=LEFT, padx=5)

        # Botão para salvar (ou apenas fechar)
        def save_and_close():
            # Se quiser persistir as cores em algum lugar, poderia salvar em JSON também
            color_window.destroy()

        close_btn = tb.Button(color_window, text="Fechar", bootstyle=PRIMARY, command=save_and_close)
        close_btn.pack(pady=10)

    # -----------------------------------------
    # 2) MÉTODO PARA SELECIONAR COLUNAS
    # -----------------------------------------
    def open_column_selector(self, view_name):
        """
        Abre uma janela que permite selecionar quais colunas serão exibidas para a 'view_name' especificada.
        Exemplo: 'Aguardando aprovação', 'Pendências', 'Pronto para pagamento'.
        """
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Configurar Colunas - {view_name}")
        sel_window.geometry("500x400")

        label = tb.Label(sel_window, text=f"Selecione as colunas para '{view_name}':", font=("Helvetica", 11, "bold"))
        label.pack(pady=10)

        # Exemplo de colunas disponíveis (poderia vir de self.app ou do constants.py)
        all_possible_columns = [
            'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
            'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
            'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
            'Telefone de contato:', 'Carimbo de data/hora_str', 'Status', 'Ultima Atualizacao', 'Valor',
            'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
            'RG/RNE:', 'Dados bancários (banco, agência e conta) '
        ]

        # Descobrimos as colunas atualmente associadas a essa view no app
        # Se você guarda em algo como self.app.custom_views[view_name] -> list:
        current_cols = self.app.custom_views.get(view_name, [])

        # Criar checkbuttons
        var_dict = {}
        for col in all_possible_columns:
            var = tb.BooleanVar(value=(col in current_cols))
            var_dict[col] = var

            def toggle_col(c=col):
                if var_dict[c].get():
                    # Marcou
                    if c not in current_cols:
                        current_cols.append(c)
                else:
                    # Desmarcou
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
            # Atualiza de fato no app
            self.app.custom_views[view_name] = current_cols
            sel_window.destroy()

        close_btn = tb.Button(sel_window, text="Salvar e Fechar", bootstyle=SUCCESS, command=close_and_save)
        close_btn.pack(pady=10)
