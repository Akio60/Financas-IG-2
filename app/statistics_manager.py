# ARQUIVO: statistics_manager.py
# Classe: StatisticsManager
# Método: show_statistics (COMPLETO E COM NOTEBOOK)

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatisticsManager:
    def __init__(self, app):
        self.app = app

    def show_statistics(self):
        """
        Exibe as estatísticas gerais em um Toplevel, usando Notebook para separar:
          - Aba 1: Texto com estatísticas
          - Aba 2: Gráfico 1 (Barras valores pagos)
          - Aba 3: Gráfico 2 (Pizza motivos)
          - Aba 4: Gráfico 3 (Pizza agência)
          - Aba 5: Gráfico 4 (Barras status)
        """
        stats_window = tb.Toplevel(self.app.root)
        stats_window.title("Estatísticas do Sistema")
        stats_window.geometry("900x700")

        data = self.app.sheets_handler.load_data()

        # Converter 'Valor' p/ float
        data['Valor'] = (
            data['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        data['Valor'] = pd.to_numeric(data['Valor'], errors='coerce').fillna(0)

        # Cálculos básicos
        total_requests = len(data)
        pending_requests = len(data[data['Status'].isin(['Autorizado', 'Aguardando documentação'])])
        awaiting_payment_requests = len(data[data['Status'] == 'Pronto para pagamento'])
        paid_requests = len(data[data['Status'] == 'Pago'])
        total_paid_values = data[data['Status'] == 'Pago']['Valor'].sum()
        total_released_values = data[data['Status'].isin(['Pago', 'Pronto para pagamento'])]['Valor'].sum()

        # Texto
        stats_text = (
            f"Número total de solicitações: {total_requests}\n"
            f"Número de solicitações pendentes: {pending_requests}\n"
            f"Número de solicitações aguardando pagamento: {awaiting_payment_requests}\n"
            f"Número de solicitações pagas: {paid_requests}\n"
            f"Soma dos valores já pagos: R$ {total_paid_values:.2f}\n"
            f"Soma dos valores já liberados: R$ {total_released_values:.2f}\n"
        )

        # ---------------------------------------
        # CRIAR NOTEBOOK (ABAS)
        # ---------------------------------------
        notebook = tb.Notebook(stats_window, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True)

        # ------------- ABA 1: TEXTO -------------
        tab_text = tb.Frame(notebook)
        notebook.add(tab_text, text="Estatísticas Gerais")

        stats_label = tb.Label(tab_text, text=stats_text, font=("Helvetica", 12), justify='left')
        stats_label.pack(pady=20, padx=20)

        # ------------- ABA 2: GRAFICO 1 -------------
        # "Valores Pagos ao Longo do Tempo"
        tab_graph1 = tb.Frame(notebook)
        notebook.add(tab_graph1, text="Valores Pagos")

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        paid_data = data[data['Status'] == 'Pago'].copy()
        if not paid_data.empty:
            paid_data['Ultima Atualizacao'] = pd.to_datetime(
                paid_data['Ultima Atualizacao'],
                format='%d/%m/%Y %H:%M:%S',
                errors='coerce'
            )
            paid_data = paid_data.dropna(subset=['Ultima Atualizacao'])
            paid_data_grouped = paid_data.groupby(paid_data['Ultima Atualizacao'].dt.date)['Valor'].sum()
            paid_data_grouped.plot(kind='bar', ax=ax1)
            ax1.set_title('Valores Pagos ao Longo do Tempo')
            ax1.set_xlabel('Data')
            ax1.set_ylabel('Valor Pago (R$)')
        else:
            ax1.text(0.5, 0.5, 'Nenhum pagamento realizado.', ha='center', va='center')
            ax1.set_title('Valores Pagos')
            ax1.axis('off')

        canvas1 = FigureCanvasTkAgg(fig1, master=tab_graph1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(pady=10)

        # ------------- ABA 3: GRAFICO 2 -------------
        # "Distribuição por Motivo"
        tab_graph2 = tb.Frame(notebook)
        notebook.add(tab_graph2, text="Motivos")

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        motivo_counts = data['Motivo da solicitação'].value_counts()
        motivo_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
        ax2.set_title('Distribuição por Motivo')
        ax2.set_ylabel('')
        canvas2 = FigureCanvasTkAgg(fig2, master=tab_graph2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(pady=10)

        # ------------- ABA 4: GRAFICO 3 -------------
        # "Distribuição por Agência de Fomento"
        tab_graph3 = tb.Frame(notebook)
        notebook.add(tab_graph3, text="Agência")

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        agencia_counts = data['Qual a agência de fomento?'].value_counts()
        agencia_counts.plot(kind='pie', ax=ax3, autopct='%1.1f%%')
        ax3.set_title('Distribuição por Agência de Fomento')
        ax3.set_ylabel('')
        canvas3 = FigureCanvasTkAgg(fig3, master=tab_graph3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(pady=10)

        # ------------- ABA 5: GRAFICO 4 -------------
        # "Solicitações por Status"
        tab_graph4 = tb.Frame(notebook)
        notebook.add(tab_graph4, text="Status")

        fig4, ax4 = plt.subplots(figsize=(6, 4))
        status_counts = data['Status'].value_counts()
        status_counts.plot(kind='bar', ax=ax4)
        ax4.set_title('Solicitações por Status')
        ax4.set_xlabel('Status')
        ax4.set_ylabel('Quantidade')
        canvas4 = FigureCanvasTkAgg(fig4, master=tab_graph4)
        canvas4.draw()
        canvas4.get_tk_widget().pack(pady=10)

        # ---------------------------------------
        # BOTÃO FECHAR
        # ---------------------------------------
        close_button = tb.Button(
            stats_window,
            text="Fechar",
            bootstyle=PRIMARY,
            command=stats_window.destroy
        )
        close_button.pack(pady=10)
