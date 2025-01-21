# settings_manager.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Text, messagebox
import os
import sys

class SettingsManager:
    def __init__(self, app):
        self.app = app
        self.settings_window = None  # Evitar várias janelas de config
        self.mask_window = None      # Janela p/ editar máscaras

    def open_settings(self):
        """Abre (ou foca) a janela de configurações."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tb.Toplevel(self.app.root)
        self.settings_window.title("Configurações")
        self.settings_window.geometry("800x500")

        main_frame = tb.Frame(self.settings_window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # COLUNA 1
        col1 = tb.Frame(main_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Título
        instructions_label = tb.Label(
            col1,
            text="Configurações (Interface / Colunas)",
            font=("Helvetica", 12, "bold")
        )
        instructions_label.grid(row=0, column=0, sticky='w', pady=5)

        # TEMA
        theme_label = tb.Label(col1, text="Selecione um tema:", font=("Helvetica", 10, "bold"))
        theme_label.grid(row=1, column=0, sticky='w', pady=5)

        themes_list = ["flatly", "darkly", "cyborg", "superhero", "cosmo"]
        theme_combo = tb.Combobox(col1, values=themes_list, state='readonly', width=25)
        theme_combo.grid(row=2, column=0, sticky='w', pady=5)

        self.app.selected_theme = self.app.selected_theme or "flatly"  # default
        theme_combo.set(self.app.selected_theme)

        # Botão "Aplicar e Reiniciar"
        def apply_and_restart():
            self.app.selected_theme = theme_combo.get()
            # Salvar em config e reiniciar
            self.app.save_selected_theme()  # define esse método no app
            # Reiniciar processo
            python = sys.executable
            os.execl(python, python, *sys.argv)

        restart_btn = tb.Button(col1, text="Aplicar e Reiniciar", bootstyle=INFO, width=25, command=apply_and_restart)
        restart_btn.grid(row=3, column=0, sticky='w', pady=5)

        # Título colunas
        columns_label = tb.Label(col1, text="Definição de Colunas", font=("Helvetica", 10, "bold"))
        columns_label.grid(row=4, column=0, sticky='w', pady=(15,5))

        # Texto explicativo
        col_txt = (
            "Selecione quais colunas serão exibidas em cada visualização\n"
            "e defina a ordem das mesmas."
        )
        col_info_label = tb.Label(col1, text=col_txt, font=("Helvetica", 9), foreground="gray")
        col_info_label.grid(row=5, column=0, sticky='w', pady=5)

        # Botões para cada view
        views = [
            ("Aguardando aprovação", "Aguardando aprovação"),
            ("Pendências", "Pendências"),
            ("Pronto para pagamento", "Pronto para pagamento")
        ]
        row_index = 6
        for label_text, view_name in views:
            btn = tb.Button(
                col1,
                text=label_text,  # removido "Editar colunas:"
                bootstyle=INFO,
                width=25,
                command=lambda v=view_name: self.open_column_selector(v)
            )
            btn.grid(row=row_index, column=0, sticky='w', pady=5)
            row_index += 1

        # COLUNA 2
        col2 = tb.Frame(main_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # E-mails
        email_section_label = tb.Label(
            col2,
            text="E-mails:",
            font=("Helvetica", 12, "bold")
        )
        email_section_label.grid(row=0, column=0, sticky='w', pady=5)

        # Instruções do email
        infobox_text = (
            "Use chaves {} para inserir dados do formulário.\n"
            "Ex.: {Nome}, {CPF:}, {Telefone de contato:}, etc."
        )
        infobox_label = tb.Label(col2, text=infobox_text, font=("Helvetica", 9), foreground="gray")
        infobox_label.grid(row=1, column=0, sticky='w', pady=5)

        row_index2 = 2
        for motivo in self.app.email_templates.keys():
            button = tb.Button(
                col2,
                text=motivo,  # removido "Editar E-mail para "
                bootstyle=SECONDARY,
                width=25,
                command=lambda m=motivo: self.edit_email_template(m)
            )
            button.grid(row=row_index2, column=0, sticky='w', pady=5)
            row_index2 += 1

        # BOTÃO editar máscaras
        mask_btn = tb.Button(col2, text="Editar Títulos de Informações", bootstyle=WARNING, width=25,
                             command=self.open_mask_editor)
        mask_btn.grid(row=row_index2, column=0, sticky='w', pady=10)
        row_index2 += 1

        # Ajusta expansões
        col1.rowconfigure(row_index, weight=1)
        col2.rowconfigure(row_index2, weight=1)

    def open_column_selector(self, view_name):
        """
        Abre janela para escolher e ordenar colunas - 2 listas: disponíveis vs selecionadas,
        com botões para mover entre elas e mudar ordem.
        """
        sel_window = tb.Toplevel(self.app.root)
        sel_window.title(f"Colunas - {view_name}")
        sel_window.geometry("700x400")

        top_label = tb.Label(sel_window, text=f"Colunas para: {view_name}", font=("Helvetica", 11, "bold"))
        top_label.pack(pady=5)

        container = tb.Frame(sel_window)
        container.pack(fill=BOTH, expand=True)

        # Colunas possíveis
        all_possible = [
            'Endereço de e-mail', 'Nome completo (sem abreviações):', 'Curso:', 'Orientador',
            'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
            'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
            'Telefone de contato:', 'Carimbo de data/hora_str', 'Status', 'Ultima Atualizacao', 'Valor',
            'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)', 'CPF:',
            'RG/RNE:', 'Dados bancários (banco, agência e conta) '
        ]

        current_cols = self.app.custom_views.get(view_name, [])

        # FRAME ESQUERDA - LISTA DE DISPONÍVEIS
        left_frame = tb.Frame(container)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        lbl_left = tb.Label(left_frame, text="Disponíveis", font=("Helvetica", 10, "bold"))
        lbl_left.pack(pady=5)

        list_avail = tb.Listbox(left_frame, selectmode='extended')
        list_avail.pack(fill=BOTH, expand=True)

        # FRAME CENTRAL - BOTÕES ->
        center_frame = tb.Frame(container)
        center_frame.pack(side=LEFT, pady=5)

        def load_lists():
            # Carrega disponíveis e selecionados
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
            # re-selecionar
            for i, idx in enumerate(sel):
                new_idx = idx - 1 if idx > 0 else 0
                list_select.selection_set(new_idx)

        def move_down():
            sel = list_select.curselection()
            if not sel:
                return
            for index in reversed(sel):
                if index == len(current_cols) -1:
                    continue
                current_cols[index], current_cols[index+1] = current_cols[index+1], current_cols[index]
            load_lists()
            # re-selecionar
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

        # FRAME DIREITA - LISTA DE SELECIONADAS
        right_frame = tb.Frame(container)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        lbl_right = tb.Label(right_frame, text="Selecionadas (ordem)", font=("Helvetica", 10, "bold"))
        lbl_right.pack(pady=5)

        list_select = tb.Listbox(right_frame, selectmode='extended')
        list_select.pack(fill=BOTH, expand=True)

        def close_and_save():
            self.app.custom_views[view_name] = current_cols
            sel_window.destroy()

        load_lists()

        close_btn = tb.Button(sel_window, text="Salvar", bootstyle=SUCCESS, command=close_and_save)
        close_btn.pack(pady=10)

    # -----------------------------------------
    # BOTÃO PARA EDITAR MÁSCARAS (FORM_FIELD_MAPPING)
    # -----------------------------------------
    def open_mask_editor(self):
        """Abre janela para editar os títulos exibidos (máscaras) individualmente."""
        if self.mask_window and self.mask_window.winfo_exists():
            self.mask_window.lift()
            return

        self.mask_window = tb.Toplevel(self.app.root)
        self.mask_window.title("Editar Títulos de Informações")
        self.mask_window.geometry("600x500")

        info_label = tb.Label(
            self.mask_window,
            text="Edite abaixo os nomes (títulos) que serão exibidos ao usuário.\n"
                 "As chaves originais (à esquerda) não podem ser alteradas, apenas o texto (valor) à direita.",
            font=("Helvetica", 9),
            foreground="gray"
        )
        info_label.pack(pady=5, padx=5)

        frame_scroll = tb.Frame(self.mask_window)
        frame_scroll.pack(fill=BOTH, expand=True, padx=10, pady=10)

        canvas = tb.Canvas(frame_scroll)
        scrollbar = tb.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0,0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.entry_vars = {}
        # A máscara está em self.app.details_manager.FORM_FIELD_MAPPING
        # ou algo similar. Vamos supor que "details_manager" tem get/set methods
        if hasattr(self.app.details_manager, 'FORM_FIELD_MAPPING'):
            field_map = self.app.details_manager.FORM_FIELD_MAPPING
        else:
            # Se definimos no details_manager de forma global, pegamos:
            field_map = self.app.details_manager.__dict__.get('FORM_FIELD_MAPPING', {})

        row_idx = 0
        for key, val in field_map.items():
            tk_label = tb.Label(scroll_frame, text=key, width=40, anchor='w')
            tk_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky='w')

            var = tb.StringVar(value=val)
            self.entry_vars[key] = var
            tk_entry = tb.Entry(scroll_frame, textvariable=var, width=40)
            tk_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky='w')

            row_idx+=1

        def save_masks():
            for k,v in self.entry_vars.items():
                field_map[k] = v.get().strip()
            messagebox.showinfo("Sucesso", "As máscaras foram atualizadas.")
            self.mask_window.destroy()

        save_btn = tb.Button(self.mask_window, text="Salvar Títulos", bootstyle=SUCCESS, command=save_masks)
        save_btn.pack(pady=5)

    def edit_email_template(self, motivo):
        """Abre janela para editar um template de email específico."""
        template_window = tb.Toplevel(self.app.root)
        template_window.title(motivo)  # removido "Editar E-mail para "
        template_window.geometry("600x400")

        label = tb.Label(
            template_window,
            text=f"Modelo de E-mail: {motivo}",
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
