import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logger_app
from logger_app import LogLevel, LogCategory

class LogViewer:
    def __init__(self, parent):
        self.window = tb.Toplevel(parent)
        self.window.title("Visualizador de Logs")
        # Maximizar a janela
        self.window.state('zoomed')
        
        self.setup_ui()
        self.load_logs()

    def _center_window(self, window, w, h):
        """Não é mais necessário para a janela de logs, mas mantido para compatibilidade"""
        pass

    def setup_ui(self):
        # Frame principal
        main_frame = tb.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de filtros
        filter_frame = tb.LabelFrame(main_frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid para filtros
        for i in range(4):
            filter_frame.columnconfigure(i, weight=1)

        # Filtro de Nível
        tb.Label(filter_frame, text="Nível:").grid(row=0, column=0, sticky='w')
        self.level_var = tk.StringVar(value="Todos")
        levels = ["Todos"] + [level.value for level in LogLevel]
        level_cb = tb.Combobox(filter_frame, textvariable=self.level_var, values=levels)
        level_cb.grid(row=1, column=0, padx=5, sticky='ew')

        # Filtro de Categoria
        tb.Label(filter_frame, text="Categoria:").grid(row=0, column=1, sticky='w')
        self.category_var = tk.StringVar(value="Todos")
        categories = ["Todos"] + [cat.value for cat in LogCategory]
        category_cb = tb.Combobox(filter_frame, textvariable=self.category_var, values=categories)
        category_cb.grid(row=1, column=1, padx=5, sticky='ew')

        # Filtro de Data
        tb.Label(filter_frame, text="Período:").grid(row=0, column=2, sticky='w')
        self.period_var = tk.StringVar(value="Últimos 7 dias")
        periods = ["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Personalizado"]
        period_cb = tb.Combobox(filter_frame, textvariable=self.period_var, values=periods)
        period_cb.grid(row=1, column=2, padx=5, sticky='ew')

        # Filtro de Usuário
        tb.Label(filter_frame, text="Usuário:").grid(row=0, column=3, sticky='w')
        self.user_var = tk.StringVar()
        user_entry = tb.Entry(filter_frame, textvariable=self.user_var)
        user_entry.grid(row=1, column=3, padx=5, sticky='ew')

        # Botões de ação
        btn_frame = tb.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tb.Button(
            btn_frame, text="Aplicar Filtros", 
            command=self.load_logs, 
            bootstyle=SUCCESS
        ).pack(side=tk.LEFT, padx=5)

        tb.Button(
            btn_frame, text="Exportar JSON", 
            command=lambda: self.export_logs('json'),
            bootstyle=INFO
        ).pack(side=tk.LEFT, padx=5)

        tb.Button(
            btn_frame, text="Exportar CSV", 
            command=lambda: self.export_logs('csv'),
            bootstyle=INFO
        ).pack(side=tk.LEFT, padx=5)

        # Treeview para logs
        columns = ("Timestamp", "Level", "Category", "User", "Action", "Details", "Status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Configurar colunas
        self.tree.heading("Timestamp", text="Data/Hora")
        self.tree.heading("Level", text="Nível")
        self.tree.heading("Category", text="Categoria")
        self.tree.heading("User", text="Usuário")
        self.tree.heading("Action", text="Ação")
        self.tree.heading("Details", text="Detalhes")
        self.tree.heading("Status", text="Status")

        # Definir larguras das colunas
        self.tree.column("Timestamp", width=150, anchor="w")
        self.tree.column("Level", width=100, anchor="center")
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("User", width=120, anchor="w")
        self.tree.column("Action", width=150, anchor="w")
        self.tree.column("Details", width=400, anchor="w")
        self.tree.column("Status", width=100, anchor="center")

        # Scrollbars
        y_scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Configurar cores por nível
        self.tree.tag_configure('ERROR', foreground='red')
        self.tree.tag_configure('SECURITY', foreground='orange')
        self.tree.tag_configure('AUDIT', foreground='blue')

    def get_date_range(self):
        period = self.period_var.get()
        end_date = datetime.now()
        
        if period == "Hoje":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Últimos 7 dias":
            start_date = end_date - timedelta(days=7)
        elif period == "Últimos 30 dias":
            start_date = end_date - timedelta(days=30)
        else:  # Personalizado
            # Aqui você pode implementar um diálogo para seleção de datas
            return None, None
            
        return start_date.strftime('%d/%m/%Y'), end_date.strftime('%d/%m/%Y')

    def load_logs(self):
        # Limpar árvore atual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Preparar filtros
        level = None if self.level_var.get() == "Todos" else LogLevel(self.level_var.get())
        category = None if self.category_var.get() == "Todos" else LogCategory(self.category_var.get())
        user = self.user_var.get() if self.user_var.get() else None
        start_date, end_date = self.get_date_range()

        # Buscar logs
        logs = logger_app.get_logs(
            level=level,
            category=category,
            start_date=start_date,
            end_date=end_date,
            user=user
        )

        # Preencher árvore
        for log in logs:
            values = (
                log['Timestamp'],
                log['Level'],
                log['Category'],
                log['User'],
                log['Action'],
                log['Details'],
                log['Status']
            )
            self.tree.insert('', 'end', values=values, tags=(log['Level'],))

    def export_logs(self, format_type):
        filetypes = [('JSON files', '*.json')] if format_type == 'json' else [('CSV files', '*.csv')]
        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=filetypes
        )
        
        if filepath:
            # Usar os mesmos filtros da visualização atual
            level = None if self.level_var.get() == "Todos" else LogLevel(self.level_var.get())
            category = None if self.category_var.get() == "Todos" else LogCategory(self.category_var.get())
            user = self.user_var.get() if self.user_var.get() else None
            start_date, end_date = self.get_date_range()

            success = logger_app.export_logs(
                filepath,
                format=format_type,
                level=level,
                category=category,
                start_date=start_date,
                end_date=end_date,
                user=user
            )

            if success:
                messagebox.showinfo("Sucesso", f"Logs exportados para {filepath}")
            else:
                messagebox.showerror("Erro", "Erro ao exportar logs")
