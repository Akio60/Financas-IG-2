# statistics_manager.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class StatisticsManager:
    def __init__(self, app):
        self.app = app

        # Vamos armazenar as referências de widgets de cada aba,
        # para não precisar de nametowidget:
        self.tab_general = None
        self.tab_barras = None
        self.tab_motivos = None
        self.tab_agencias = None

        self.frame_barras = None
        self.frame_motivos = None
        self.frame_agencias = None
        self.label_general_stats = None

    def show_statistics(self):
        """
        Abre uma janela (Toplevel) com 4 abas (Notebook):
          - Aba 1: Estatísticas gerais
          - Aba 2: Gráfico de barras (valores pagos ao longo do tempo)
          - Aba 3: Motivos de pedido (pizza)
          - Aba 4: Agências de fomento (pizza)
        Cada aba tem um campo Data Início, Data Fim e um botão Filtrar.
        """
        stats_window = tb.Toplevel(self.app.root)
        stats_window.title("Estatísticas do Sistema")
        stats_window.geometry("900x700")

        # Cria Notebook
        notebook = tb.Notebook(stats_window, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True)

        # ----------- ABA 1: Estatísticas gerais -----------
        self.tab_general = tb.Frame(notebook)
        notebook.add(self.tab_general, text="Estatísticas Gerais")
        self._add_date_filter_widgets(self.tab_general, self._filter_general_stats)

        self.label_general_stats = tb.Label(self.tab_general, text="", font=("Helvetica", 12), justify='left')
        self.label_general_stats.pack(pady=20, padx=20)

        # ----------- ABA 2: Gráfico de barras -----------
        self.tab_barras = tb.Frame(notebook)
        notebook.add(self.tab_barras, text="Valores Pagos")
        self._add_date_filter_widgets(self.tab_barras, self._filter_barras)

        self.frame_barras = tb.Frame(self.tab_barras)
        self.frame_barras.pack(fill=BOTH, expand=True)

        # ----------- ABA 3: Motivos de pedido (pizza) -----------
        self.tab_motivos = tb.Frame(notebook)
        notebook.add(self.tab_motivos, text="Motivos de Pedido")
        self._add_date_filter_widgets(self.tab_motivos, self._filter_motivos)

        self.frame_motivos = tb.Frame(self.tab_motivos)
        self.frame_motivos.pack(fill=BOTH, expand=True)

        # ----------- ABA 4: Agências de fomento (pizza) -----------
        self.tab_agencias = tb.Frame(notebook)
        notebook.add(self.tab_agencias, text="Agências de Fomento")
        self._add_date_filter_widgets(self.tab_agencias, self._filter_agencias)

        self.frame_agencias = tb.Frame(self.tab_agencias)
        self.frame_agencias.pack(fill=BOTH, expand=True)

        # Botão para fechar a janela
        close_button = tb.Button(
            stats_window,
            text="Fechar",
            bootstyle=PRIMARY,
            command=stats_window.destroy
        )
        close_button.pack(pady=10)

        # Chama inicialmente sem filtro
        self._filter_general_stats()
        self._filter_barras()
        self._filter_motivos()
        self._filter_agencias()

    # -------------------------------------------------------------
    # FUNÇÕES AUXILIARES PARA CRIAR OS CAMPOS DE DATA E FILTRO
    # -------------------------------------------------------------
    def _add_date_filter_widgets(self, parent_frame, filter_callback):
        """
        Cria 2 tb.Entry (Data Início, Data Fim) e um tb.Button (Filtrar).
        Armazena as entries como atributos do parent_frame.
        """
        filter_frame = tb.Frame(parent_frame)
        filter_frame.pack(pady=10, fill=X)

        start_label = tb.Label(filter_frame, text="Data Início (dd/mm/aaaa):")
        start_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        start_entry = tb.Entry(filter_frame, width=12)
        start_entry.grid(row=0, column=1, padx=5, pady=5)

        end_label = tb.Label(filter_frame, text="Data Fim (dd/mm/aaaa):")
        end_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        end_entry = tb.Entry(filter_frame, width=12)
        end_entry.grid(row=0, column=3, padx=5, pady=5)

        def do_filter():
            filter_callback(start_entry.get().strip(), end_entry.get().strip())

        filter_button = tb.Button(filter_frame, text="Filtrar", bootstyle=INFO, command=do_filter)
        filter_button.grid(row=0, column=4, padx=10, pady=5)

        # Armazena as entries no parent_frame
        parent_frame.start_entry = start_entry
        parent_frame.end_entry = end_entry

    def _parse_dates(self, str_inicio, str_fim):
        """
        Converte as strings em datas datetime ou None se inválido.
        Formato esperado: dd/mm/aaaa
        """
        fmt = "%d/%m/%Y"
        start_date = None
        end_date = None

        if str_inicio:
            try:
                start_date = datetime.strptime(str_inicio, fmt)
            except ValueError:
                pass

        if str_fim:
            try:
                end_date = datetime.strptime(str_fim, fmt)
            except ValueError:
                pass

        return start_date, end_date

    def _filter_dataframe_by_date(self, df, start_date, end_date):
        """
        Filtra o DF pelo campo 'Carimbo de data/hora' no intervalo [start_date, end_date].
        """
        df['Carimbo de data/hora'] = pd.to_datetime(
            df['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )

        if start_date is not None:
            df = df[df['Carimbo de data/hora'] >= start_date]
        if end_date is not None:
            # para incluir o dia fim completo
            df = df[df['Carimbo de data/hora'] <= end_date]

        return df

    # -------------------------------------------------------------
    # ABA 1: Estatísticas gerais
    # -------------------------------------------------------------
    def _filter_general_stats(self, str_inicio=None, str_fim=None):
        if not self.tab_general:
            return

        if str_inicio is None or str_fim is None:
            str_inicio = self.tab_general.start_entry.get().strip()
            str_fim = self.tab_general.end_entry.get().strip()

        start_date, end_date = self._parse_dates(str_inicio, str_fim)

        data = self.app.sheets_handler.load_data()
        data = self._filter_dataframe_by_date(data, start_date, end_date)

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

    # -------------------------------------------------------------
    # ABA 2: Gráfico de barras
    # -------------------------------------------------------------
    def _filter_barras(self, str_inicio=None, str_fim=None):
        if not self.tab_barras:
            return

        if str_inicio is None or str_fim is None:
            str_inicio = self.tab_barras.start_entry.get().strip()
            str_fim = self.tab_barras.end_entry.get().strip()

        start_date, end_date = self._parse_dates(str_inicio, str_fim)

        data = self.app.sheets_handler.load_data()
        data = self._filter_dataframe_by_date(data, start_date, end_date)

        data['Valor'] = (
            data['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        data['Valor'] = pd.to_numeric(data['Valor'], errors='coerce').fillna(0)

        # Limpa o frame
        for w in self.frame_barras.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6,4))
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

    # -------------------------------------------------------------
    # ABA 3: Motivos de pedido (pizza)
    # -------------------------------------------------------------
    def _filter_motivos(self, str_inicio=None, str_fim=None):
        if not self.tab_motivos:
            return

        if str_inicio is None or str_fim is None:
            str_inicio = self.tab_motivos.start_entry.get().strip()
            str_fim = self.tab_motivos.end_entry.get().strip()

        start_date, end_date = self._parse_dates(str_inicio, str_fim)
        data = self.app.sheets_handler.load_data()
        data = self._filter_dataframe_by_date(data, start_date, end_date)

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

    # -------------------------------------------------------------
    # ABA 4: Agências de fomento (pizza)
    # -------------------------------------------------------------
    def _filter_agencias(self, str_inicio=None, str_fim=None):
        if not self.tab_agencias:
            return

        if str_inicio is None or str_fim is None:
            str_inicio = self.tab_agencias.start_entry.get().strip()
            str_fim = self.tab_agencias.end_entry.get().strip()

        start_date, end_date = self._parse_dates(str_inicio, str_fim)
        data = self.app.sheets_handler.load_data()
        data = self._filter_dataframe_by_date(data, start_date, end_date)

        for w in self.frame_agencias.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6,4))
        agencia_counts = data['Qual a agência de fomento?'].value_counts()
        if not agencia_counts.empty:
            agencia_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title('Distribuição por Agência de Fomento')
            ax.set_ylabel('')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado no período', ha='center', va='center')
            ax.set_title('Agências de Fomento')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.frame_agencias)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
