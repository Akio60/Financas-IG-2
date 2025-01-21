# statistics_manager.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, date

class StatisticsManager:
    def __init__(self, app):
        self.app = app
        self.stats_window = None  # referência para evitar janelas duplicadas

    def show_statistics(self):
        """
        Exibe (ou foca) a janela de estatísticas em um Toplevel com 4 abas:
          - Estatísticas gerais
          - Gráfico de barras (valores pagos)
          - Motivos (pizza)
          - Agências (pizza)
        Cada aba tem radio buttons para (mês atual, este semestre, este ano, personalizado).
        Se personalizado, exibe combo boxes de data início e data fim.
        """
        # Se a janela já existir, apenas foca
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            return

        self.stats_window = tb.Toplevel(self.app.root)
        self.stats_window.title("Estatísticas do Sistema")
        self.stats_window.geometry("950x750")

        notebook = tb.Notebook(self.stats_window, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True)

        # ABA 1: Estatísticas gerais
        self.tab_general = tb.Frame(notebook)
        notebook.add(self.tab_general, text="Estatísticas Gerais")

        self._build_period_selector(self.tab_general, self._filter_general_stats)

        self.label_general_stats = tb.Label(self.tab_general, text="", font=("Helvetica", 12), justify='left')
        self.label_general_stats.pack(pady=20, padx=20)

        # ABA 2: Barras
        self.tab_barras = tb.Frame(notebook)
        notebook.add(self.tab_barras, text="Valores Pagos")

        self._build_period_selector(self.tab_barras, self._filter_barras)
        self.frame_barras = tb.Frame(self.tab_barras)
        self.frame_barras.pack(fill=BOTH, expand=True)

        # ABA 3: Motivos
        self.tab_motivos = tb.Frame(notebook)
        notebook.add(self.tab_motivos, text="Motivos")

        self._build_period_selector(self.tab_motivos, self._filter_motivos)
        self.frame_motivos = tb.Frame(self.tab_motivos)
        self.frame_motivos.pack(fill=BOTH, expand=True)

        # ABA 4: Agências
        self.tab_agencias = tb.Frame(notebook)
        notebook.add(self.tab_agencias, text="Agências")

        self._build_period_selector(self.tab_agencias, self._filter_agencias)
        self.frame_agencias = tb.Frame(self.tab_agencias)
        self.frame_agencias.pack(fill=BOTH, expand=True)

        close_button = tb.Button(
            self.stats_window,
            text="Fechar",
            bootstyle=PRIMARY,
            command=self.stats_window.destroy
        )
        close_button.pack(pady=10)

        # Inicial
        self._filter_general_stats()
        self._filter_barras()
        self._filter_motivos()
        self._filter_agencias()

    # -----------------------------------------------------------
    # BUILD PERIOD SELECTOR (mês atual, semestre, ano, personal)
    # -----------------------------------------------------------
    def _build_period_selector(self, parent_frame, filter_func):
        """
        Cria radio buttons para (mês atual, semestre, ano, personalizado)
        e, se personalizado, exibe combo boxes de data início/fim.
        """
        period_frame = tb.Frame(parent_frame)
        period_frame.pack(fill=X, pady=10)

        self_var = tb.StringVar(value="mes")  # default: mês atual

        # Radios
        radios = [
            ("Mês atual", "mes"),
            ("Este semestre", "semestre"),
            ("Este ano", "ano"),
            ("Personalizado", "custom")
        ]
        col=0
        for label, val in radios:
            rb = tb.Radiobutton(period_frame, text=label, variable=self_var, value=val)
            rb.grid(row=0, column=col, padx=5, pady=5, sticky='w')
            col+=1

        # Combos de data início e fim
        date_frame = tb.Frame(period_frame)
        date_frame.grid(row=1, column=0, columnspan=4, sticky='w')

        # Dia / Mês / Ano
        days = [str(i).zfill(2) for i in range(1,32)]
        months = [str(i).zfill(2) for i in range(1,13)]
        years = [str(y) for y in range(2020, 2035)]

        # Início
        lbl_start = tb.Label(date_frame, text="Início:")
        lbl_start.grid(row=0, column=0, padx=5, sticky='e')

        day_start = tb.Combobox(date_frame, values=days, width=3, state='readonly')
        month_start = tb.Combobox(date_frame, values=months, width=3, state='readonly')
        year_start = tb.Combobox(date_frame, values=years, width=5, state='readonly')

        day_start.grid(row=0, column=1, padx=2)
        month_start.grid(row=0, column=2, padx=2)
        year_start.grid(row=0, column=3, padx=2)

        # Fim
        lbl_end = tb.Label(date_frame, text="Fim:")
        lbl_end.grid(row=0, column=4, padx=5, sticky='e')

        day_end = tb.Combobox(date_frame, values=days, width=3, state='readonly')
        month_end = tb.Combobox(date_frame, values=months, width=3, state='readonly')
        year_end = tb.Combobox(date_frame, values=years, width=5, state='readonly')

        day_end.grid(row=0, column=5, padx=2)
        month_end.grid(row=0, column=6, padx=2)
        year_end.grid(row=0, column=7, padx=2)

        # Botão filtrar
        def do_filter():
            filter_func(self_var.get(), day_start.get(), month_start.get(), year_start.get(),
                        day_end.get(), month_end.get(), year_end.get())

        filter_btn = tb.Button(date_frame, text="Filtrar", bootstyle=INFO, command=do_filter)
        filter_btn.grid(row=0, column=8, padx=10)

        # Armazena
        parent_frame.period_var = self_var
        parent_frame.day_start = day_start
        parent_frame.month_start = month_start
        parent_frame.year_start = year_start
        parent_frame.day_end = day_end
        parent_frame.month_end = month_end
        parent_frame.year_end = year_end

    # -----------------------------------------------------------
    # FUNÇÕES DE FILTRO DE DATA
    # -----------------------------------------------------------
    def _apply_period(self, df, period, ds, ms, ys, de, me, ye):
        """
        Aplica o período ao DataFrame, retornando DataFrame filtrado
        period: 'mes', 'semestre', 'ano', 'custom'
        ds/ms/ys: dia, mes, ano da data início (strings)
        de/me/ye: dia, mes, ano da data fim
        """
        # Converte 'Carimbo de data/hora'
        df['Carimbo de data/hora'] = pd.to_datetime(
            df['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )

        if period == 'mes':
            # mês atual
            now = date.today()
            start_date = datetime(now.year, now.month, 1)
            # fim do mês
            if now.month == 12:
                end_date = datetime(now.year, 12, 31, 23, 59, 59)
            else:
                # Calcula próximo mês - 1 dia
                nxt_month = date(now.year, now.month+1, 1)
                end_date = datetime(nxt_month.year, nxt_month.month, 1, 23, 59, 59) - pd.Timedelta(days=1)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        elif period == 'semestre':
            now = date.today()
            if now.month <= 6:
                # 1º semestre
                start_date = datetime(now.year, 1, 1)
                end_date = datetime(now.year, 6, 30, 23, 59, 59)
            else:
                # 2º semestre
                start_date = datetime(now.year, 7, 1)
                end_date = datetime(now.year, 12, 31, 23, 59, 59)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        elif period == 'ano':
            now = date.today()
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31, 23, 59, 59)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        else:
            # custom
            start_date, end_date = None, None
            try:
                dd = int(ds)
                mm = int(ms)
                yy = int(ys)
                start_date = datetime(yy, mm, dd)
            except:
                pass
            try:
                dd2 = int(de)
                mm2 = int(me)
                yy2 = int(ye)
                end_date = datetime(yy2, mm2, dd2, 23, 59, 59)
            except:
                pass
            if start_date is not None:
                df = df[df['Carimbo de data/hora'] >= start_date]
            if end_date is not None:
                df = df[df['Carimbo de data/hora'] <= end_date]
            return df

    # -------------------------------------------------------------
    # ABA 1: Estatísticas gerais
    # -------------------------------------------------------------
    def _filter_general_stats(self, period=None, ds=None, ms=None, ys=None, de=None, me=None, ye=None):
        if not hasattr(self, 'tab_general'):
            return
        if period is None:
            period = self.tab_general.period_var.get()
            ds = self.tab_general.day_start.get()
            ms = self.tab_general.month_start.get()
            ys = self.tab_general.year_start.get()
            de = self.tab_general.day_end.get()
            me = self.tab_general.month_end.get()
            ye = self.tab_general.year_end.get()

        data = self.app.sheets_handler.load_data()
        data = self._apply_period(data, period, ds, ms, ys, de, me, ye)

        data['Valor'] = (
            data['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        data['Valor'] = pd.to_numeric(data['Valor'], errors='coerce').fillna(0)

        total_requests = len(data)
        pending_requests = len(data[data['Status'].isin(['Autorizado', 'Aguardando documentação'])])
        awaiting_payment_requests = len(data[data['Status'] == 'Pronto para pagamento'])
        paid_requests = len(data[data['Status'] == 'Pago'])
        total_paid_values = data[data['Status'] == 'Pago']['Valor'].sum()
        total_released_values = data[data['Status'].isin(['Pago', 'Pronto para pagamento'])]['Valor'].sum()

        stats_text = (
            f"Número total de solicitações: {total_requests}\n"
            f"Número de solicitações pendentes: {pending_requests}\n"
            f"Número de solicitações aguardando pagamento: {awaiting_payment_requests}\n"
            f"Número de solicitações pagas: {paid_requests}\n"
            f"Soma dos valores já pagos: R$ {total_paid_values:.2f}\n"
            f"Soma dos valores já liberados: R$ {total_released_values:.2f}\n"
        )
        self.label_general_stats.config(text=stats_text)

    def _filter_barras(self, period=None, ds=None, ms=None, ys=None, de=None, me=None, ye=None):
        if not hasattr(self, 'tab_barras'):
            return
        if period is None:
            period = self.tab_barras.period_var.get()
            ds = self.tab_barras.day_start.get()
            ms = self.tab_barras.month_start.get()
            ys = self.tab_barras.year_start.get()
            de = self.tab_barras.day_end.get()
            me = self.tab_barras.month_end.get()
            ye = self.tab_barras.year_end.get()

        data = self.app.sheets_handler.load_data()
        data = self._apply_period(data, period, ds, ms, ys, de, me, ye)

        for w in self.frame_barras.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6,4))
        data['Valor'] = (
            data['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        data['Valor'] = pd.to_numeric(data['Valor'], errors='coerce').fillna(0)
        paid_data = data[data['Status'] == 'Pago'].copy()
        paid_data['Ultima Atualizacao'] = pd.to_datetime(
            paid_data['Ultima Atualizacao'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        paid_data = paid_data.dropna(subset=['Ultima Atualizacao'])

        if not paid_data.empty:
            paid_data_grouped = paid_data.groupby(paid_data['Ultima Atualizacao'].dt.date)['Valor'].sum()
            paid_data_grouped.plot(kind='bar', ax=ax)
            ax.set_title('Valores Pagos ao Longo do Tempo')
            ax.set_xlabel('Data')
            ax.set_ylabel('Valor Pago (R$)')
        else:
            ax.text(0.5, 0.5, 'Nenhum pagamento realizado nesse período.', ha='center', va='center')
            ax.set_title('Valores Pagos')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.frame_barras)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def _filter_motivos(self, period=None, ds=None, ms=None, ys=None, de=None, me=None, ye=None):
        if not hasattr(self, 'tab_motivos'):
            return
        if period is None:
            period = self.tab_motivos.period_var.get()
            ds = self.tab_motivos.day_start.get()
            ms = self.tab_motivos.month_start.get()
            ys = self.tab_motivos.year_start.get()
            de = self.tab_motivos.day_end.get()
            me = self.tab_motivos.month_end.get()
            ye = self.tab_motivos.year_end.get()

        data = self.app.sheets_handler.load_data()
        data = self._apply_period(data, period, ds, ms, ys, de, me, ye)

        for w in self.frame_motivos.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6,4))
        motivo_counts = data['Motivo da solicitação'].value_counts()
        if not motivo_counts.empty:
            motivo_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title('Distribuição por Motivo')
            ax.set_ylabel('')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado no período', ha='center', va='center')
            ax.set_title('Motivos')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.frame_motivos)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def _filter_agencias(self, period=None, ds=None, ms=None, ys=None, de=None, me=None, ye=None):
        if not hasattr(self, 'tab_agencias'):
            return
        if period is None:
            period = self.tab_agencias.period_var.get()
            ds = self.tab_agencias.day_start.get()
            ms = self.tab_agencias.month_start.get()
            ys = self.tab_agencias.year_start.get()
            de = self.tab_agencias.day_end.get()
            me = self.tab_agencias.month_end.get()
            ye = self.tab_agencias.year_end.get()

        data = self.app.sheets_handler.load_data()
        data = self._apply_period(data, period, ds, ms, ys, de, me, ye)

        for w in self.frame_agencias.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6,4))
        agencia_counts = data['Qual a agência de fomento?'].value_counts()
        if not agencia_counts.empty:
            agencia_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title('Distribuição por Agência')
            ax.set_ylabel('')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado no período', ha='center', va='center')
            ax.set_title('Agências de Fomento')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.frame_agencias)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
