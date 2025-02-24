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
        self.setup_summary_frame()
        self.setup_search_frame()

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

        # Modificar o callback do combobox de período
        period_cb.bind('<<ComboboxSelected>>', lambda e: self.on_period_change())

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

    def setup_summary_frame(self):
        """Adiciona frame com resumo estatístico"""
        summary_frame = tb.LabelFrame(self.window, text="Resumo", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        stats = logger_app.get_summary_stats()
        
        for i, (key, value) in enumerate(stats.items()):
            label_text = key.replace('_', ' ').title()
            if 'rate' in key.lower():
                value = f"{value:.1f}%"
            tb.Label(summary_frame, 
                    text=f"{label_text}: {value}",
                    font=("Helvetica", 10, "bold")).grid(row=0, column=i, padx=20)

    def setup_search_frame(self):
        """Adiciona campo de busca por palavra-chave"""
        search_frame = tb.Frame(self.window, padding=5)
        search_frame.pack(fill=tk.X)

        self.search_var = tk.StringVar()
        search_entry = tb.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        def do_search():
            keyword = self.search_var.get().strip()
            if keyword:
                logs = logger_app.search_by_keyword(
                    keyword,
                    level=None if self.level_var.get() == "Todos" else LogLevel(self.level_var.get()),
                    category=None if self.category_var.get() == "Todos" else LogCategory(self.category_var.get())
                )
                self.update_treeview(logs)
            else:
                self.load_logs()  # Recarrega todos os logs

        search_btn = tb.Button(
            search_frame,
            text="Buscar",
            bootstyle=INFO,
            command=do_search
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tb.Button(
            search_frame,
            text="Limpar",
            bootstyle=SECONDARY,
            command=lambda: [self.search_var.set(''), self.load_logs()]
        )
        clear_btn.pack(side=tk.LEFT)

    def update_treeview(self, logs):
        """Atualiza a treeview com os logs fornecidos"""
        self.tree.delete(*self.tree.get_children())
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

    def get_date_range(self):
        """Retorna o intervalo de datas baseado no período selecionado"""
        period = self.period_var.get()
        end_date = datetime.now()
        
        if period == "Hoje":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Últimos 7 dias":
            start_date = end_date - timedelta(days=7)
        elif period == "Últimos 30 dias":
            start_date = end_date - timedelta(days=30)
        elif period == "Personalizado":
            if not hasattr(self, 'custom_start_date'):
                self.show_date_picker()
                return None, None
            
            try:
                start_date = datetime.strptime(self.custom_start_date, '%d/%m/%Y')
                end_date = datetime.strptime(self.custom_end_date, '%d/%m/%Y')
                return self.custom_start_date, self.custom_end_date
            except (AttributeError, ValueError):
                self.show_date_picker()
                return None, None
            
        return start_date.strftime('%d/%m/%Y'), end_date.strftime('%d/%m/%Y')

    def show_date_picker(self):
        """Mostra diálogo para seleção de período personalizado"""
        date_window = tb.Toplevel(self.window)
        date_window.title("Selecionar Período")
        date_window.attributes('-topmost', True)
        
        # Centraliza a janela
        w, h = 400, 250
        ws = date_window.winfo_screenwidth()
        hs = date_window.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        date_window.geometry(f"{w}x{h}+{x}+{y}")
        
        # Impede redimensionamento
        date_window.resizable(False, False)
        
        # Frame principal
        main_frame = tb.Frame(date_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para data inicial
        start_frame = tb.LabelFrame(main_frame, text="Data Inicial (DD/MM/AAAA)", padding=10)
        start_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Entradas separadas para dia, mês e ano - Data Inicial
        start_day = tb.Entry(start_frame, width=3)
        start_day.pack(side=tk.LEFT, padx=2)
        tb.Label(start_frame, text="/").pack(side=tk.LEFT)
        
        start_month = tb.Entry(start_frame, width=3)
        start_month.pack(side=tk.LEFT, padx=2)
        tb.Label(start_frame, text="/").pack(side=tk.LEFT)
        
        start_year = tb.Entry(start_frame, width=5)
        start_year.pack(side=tk.LEFT, padx=2)
        
        # Frame para data final
        end_frame = tb.LabelFrame(main_frame, text="Data Final (DD/MM/AAAA)", padding=10)
        end_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Entradas separadas para dia, mês e ano - Data Final
        end_day = tb.Entry(end_frame, width=3)
        end_day.pack(side=tk.LEFT, padx=2)
        tb.Label(end_frame, text="/").pack(side=tk.LEFT)
        
        end_month = tb.Entry(end_frame, width=3)
        end_month.pack(side=tk.LEFT, padx=2)
        tb.Label(end_frame, text="/").pack(side=tk.LEFT)
        
        end_year = tb.Entry(end_frame, width=5)
        end_year.pack(side=tk.LEFT, padx=2)

        def validate_date(day, month, year):
            try:
                if not (1 <= int(day) <= 31 and 1 <= int(month) <= 12 and 1000 <= int(year) <= 9999):
                    return False
                datetime(int(year), int(month), int(day))
                return True
            except ValueError:
                return False

        def validate_and_close():
            try:
                # Validar data inicial
                if not validate_date(start_day.get(), start_month.get(), start_year.get()):
                    messagebox.showerror("Erro", "Data inicial inválida!")
                    return
                
                # Validar data final
                if not validate_date(end_day.get(), end_month.get(), end_year.get()):
                    messagebox.showerror("Erro", "Data final inválida!")
                    return
                
                # Criar objetos datetime para comparação
                start = datetime(
                    int(start_year.get()),
                    int(start_month.get()),
                    int(start_day.get())
                )
                end = datetime(
                    int(end_year.get()),
                    int(end_month.get()),
                    int(end_day.get())
                )
                
                if start > end:
                    messagebox.showerror("Erro", "Data inicial não pode ser maior que a data final!")
                    return
                    
                if end > datetime.now():
                    messagebox.showerror("Erro", "Data final não pode ser maior que hoje!")
                    return
                
                self.custom_start_date = start.strftime('%d/%m/%Y')
                self.custom_end_date = end.strftime('%d/%m/%Y')
                date_window.destroy()
                self.load_logs()  # Recarrega os logs com o novo período
                
            except ValueError as e:
                messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA")

        # Frame para botões
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Adiciona os botões
        tb.Button(
            btn_frame,
            text="Confirmar",
            bootstyle=SUCCESS,
            command=validate_and_close
        ).pack(side=tk.LEFT, padx=5, expand=True)
        
        tb.Button(
            btn_frame,
            text="Cancelar",
            bootstyle=DANGER,
            command=date_window.destroy
        ).pack(side=tk.LEFT, padx=5, expand=True)

        # Preenche com a data atual
        today = datetime.now()
        end_day.insert(0, today.strftime('%d'))
        end_month.insert(0, today.strftime('%m'))
        end_year.insert(0, today.strftime('%Y'))
        
        # Data inicial como 30 dias atrás
        start_date = today - timedelta(days=30)
        start_day.insert(0, start_date.strftime('%d'))
        start_month.insert(0, start_date.strftime('%m'))
        start_year.insert(0, start_date.strftime('%Y'))

    def on_period_change(self):
        """Callback quando o período é alterado"""
        if self.period_var.get() == "Personalizado":
            self.show_date_picker()
        else:
            self.load_logs()

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
