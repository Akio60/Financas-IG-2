import os
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Ajuste estes imports conforme sua estrutura
# from google_sheets_handler import GoogleSheetsHandler

# Ajuste se quiser que a cor do retângulo central seja "cinza"
# e o fundo seja "#2C3E50".

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Vitor Akio\Desktop\graph\build\assets\frame0")

BASE_DIR = Path(__file__).resolve().parent
#ASSETS_PATH = BASE_DIR / "images" / "graph_view"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class StatisticsManager:
    def __init__(self, app):
        self.app = app  # para acessar self.app.sheets_handler etc.

        # Armazena o Toplevel (janela de estatísticas) e o Frame de gráfico
        self.stats_window = None
        self.graph_frame = None

        # Estado atual: qual "período" e qual "tipo" de estatística
        self.current_period = "mes"  # "mes", "semestre", "ano", "total", "custom"
        self.current_stat_type = "geral"  # "geral", "barras", "motivos", "agencias"

        # Para armazenar os botões (caso queira mudar estilo ao clicar)
        self.top_buttons = {}
        self.left_buttons = {}

    def show_statistics(self):
        """Abre (ou foca) a janela no novo layout do Tkinter Designer."""
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            return

        # Cria a janela
        self.stats_window = tb.Toplevel(self.app.root)
        self.stats_window.title("Estatísticas - Novo Layout")
        self.stats_window.geometry("1000x750")
        self.stats_window.configure(bg="#FFFFFF")

        # Canvas de fundo (com retângulo azul e retângulo cinza)
        self.canvas = tb.Canvas(
            self.stats_window,
            bg="#FFFFFF",
            height=750,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Fundo azul
        self.canvas.create_rectangle(
            0.0, 0.0,
            1000.0, 750.0,
            fill="#2C3E50",
            outline=""
        )

        # Retângulo cinza na parte central (para referência):
        self.canvas.create_rectangle(
            235.0, 158.0,
            940.0, 696.0,
            fill="#D9D9D9",
            outline=""
        )

        # Frame (outra forma) em cima do retângulo
        # Neste frame exibiremos os gráficos ou texto
        self.graph_frame = tb.Frame(self.stats_window, width=705, height=538)
        self.graph_frame.place(x=235, y=158)

        # Adiciona a imagem do logo (opcional)
        try:
            image_1 = tb.PhotoImage(file=relative_to_assets("image_1.png"))
            self.canvas.create_image(94.0, 85.0, image=image_1)
            # Para evitar garbage collection:
            self.logo_img_ref = image_1
        except:
            pass

        # ============ BOTÕES DO TOPO (Período) ============
        # 1) Último mês
        btn1_img = tb.PhotoImage(file=relative_to_assets("button_1.png"))
        btn1 = tb.Button(
            self.stats_window,
            image=btn1_img,
            command=lambda: self.set_period("mes"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn1.place(x=174.0, y=65.0, width=147.0, height=40.0)
        self.top_buttons["mes"] = (btn1, btn1_img)

        # 2) Último Semestre
        btn2_img = tb.PhotoImage(file=relative_to_assets("button_2.png"))
        btn2 = tb.Button(
            self.stats_window,
            image=btn2_img,
            command=lambda: self.set_period("semestre"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn2.place(x=338.0, y=65.0, width=147.0, height=40.0)
        self.top_buttons["semestre"] = (btn2, btn2_img)

        # 3) Último Ano
        btn3_img = tb.PhotoImage(file=relative_to_assets("button_3.png"))
        btn3 = tb.Button(
            self.stats_window,
            image=btn3_img,
            command=lambda: self.set_period("ano"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn3.place(x=502.0, y=65.0, width=147.0, height=40.0)
        self.top_buttons["ano"] = (btn3, btn3_img)

        # 4) Total
        btn4_img = tb.PhotoImage(file=relative_to_assets("button_4.png"))
        btn4 = tb.Button(
            self.stats_window,
            image=btn4_img,
            command=lambda: self.set_period("total"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn4.place(x=666.0, y=65.0, width=147.0, height=40.0)
        self.top_buttons["total"] = (btn4, btn4_img)

        # 5) Personalizado
        btn5_img = tb.PhotoImage(file=relative_to_assets("button_5.png"))
        btn5 = tb.Button(
            self.stats_window,
            image=btn5_img,
            command=lambda: self.set_period("custom"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn5.place(x=830.0, y=65.0, width=147.0, height=40.0)
        self.top_buttons["custom"] = (btn5, btn5_img)

        # ============ BOTÕES LATERAIS (Tipo de Estatística) ============
        # 1) Estatísticas Gerais
        btn6_img = tb.PhotoImage(file=relative_to_assets("button_6.png"))
        btn6 = tb.Button(
            self.stats_window,
            image=btn6_img,
            command=lambda: self.set_stat_type("geral"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn6.place(x=19.0, y=175.0, width=150.0, height=40.0)
        self.left_buttons["geral"] = (btn6, btn6_img)

        # 2) Valores Pagos (Barras)
        btn7_img = tb.PhotoImage(file=relative_to_assets("button_7.png"))
        btn7 = tb.Button(
            self.stats_window,
            image=btn7_img,
            command=lambda: self.set_stat_type("barras"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn7.place(x=19.0, y=236.0, width=150.0, height=40.0)
        self.left_buttons["barras"] = (btn7, btn7_img)

        # 3) Motivos
        btn8_img = tb.PhotoImage(file=relative_to_assets("button_8.png"))
        btn8 = tb.Button(
            self.stats_window,
            image=btn8_img,
            command=lambda: self.set_stat_type("motivos"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn8.place(x=19.0, y=297.0, width=150.0, height=40.0)
        self.left_buttons["motivos"] = (btn8, btn8_img)

        # 4) Agências
        btn9_img = tb.PhotoImage(file=relative_to_assets("button_9.png"))
        btn9 = tb.Button(
            self.stats_window,
            image=btn9_img,
            command=lambda: self.set_stat_type("agencias"),
            borderwidth=0,
            highlightthickness=0,
            bootstyle=(SECONDARY),
            relief="flat"
        )
        btn9.place(x=19.0, y=656.0, width=150.0, height=40.0)
        self.left_buttons["agencias"] = (btn9, btn9_img)

        # Carrega dados iniciais
        self.redraw_chart()

    # ----------------------------
    # Muda o período atual e redesenha
    # ----------------------------
    def set_period(self, period):
        self.current_period = period
        # Se "custom", poderíamos abrir combos, mas aqui simplificamos
        self.redraw_chart()

    # ----------------------------
    # Muda o tipo de estatística e redesenha
    # ----------------------------
    def set_stat_type(self, stype):
        self.current_stat_type = stype
        self.redraw_chart()

    # ----------------------------
    # Rotina central que aplica filtragem e chama
    # a função de desenho correspondente
    # ----------------------------
    def redraw_chart(self):
        # 1) Carregar DF e aplicar período
        df = self.app.sheets_handler.load_data()

        # Aplica a filtragem
        df = self._apply_period_filter(df)

        # 2) Limpamos o graph_frame
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # 3) Chamamos a função certa
        if self.current_stat_type == "geral":
            self.draw_geral_stats(df)
        elif self.current_stat_type == "barras":
            self.draw_barras(df)
        elif self.current_stat_type == "motivos":
            self.draw_motivos(df)
        elif self.current_stat_type == "agencias":
            self.draw_agencias(df)

    # ----------------------------
    # Aplica o período "mes", "semestre", "ano", "total", "custom"
    # (similar ao _apply_period do antigo)
    # ----------------------------
    def _apply_period_filter(self, df):
        df['Carimbo de data/hora'] = pd.to_datetime(
            df['Carimbo de data/hora'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        now = date.today()
        if self.current_period == "mes":
            start_date = datetime(now.year, now.month, 1)
            if now.month == 12:
                end_date = datetime(now.year, 12, 31, 23, 59, 59)
            else:
                nxt_month = date(now.year, now.month+1, 1)
                end_date = datetime(nxt_month.year, nxt_month.month, 1, 23, 59, 59) - pd.Timedelta(days=1)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        elif self.current_period == "semestre":
            if now.month <= 6:
                start_date = datetime(now.year, 1, 1)
                end_date = datetime(now.year, 6, 30, 23, 59, 59)
            else:
                start_date = datetime(now.year, 7, 1)
                end_date = datetime(now.year, 12, 31, 23, 59, 59)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        elif self.current_period == "ano":
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31, 23, 59, 59)
            mask = (df['Carimbo de data/hora'] >= start_date) & (df['Carimbo de data/hora'] <= end_date)
            return df[mask]

        elif self.current_period == "total":
            # sem filtro
            return df

        else:
            # custom - poderia abrir combos para data start/end
            # mas aqui, sem combos, retornamos df normal
            return df

    # ----------------------------
    # Funções de desenho
    # ----------------------------
    def draw_geral_stats(self, df):
        # Calcular estatísticas e exibir como texto ou fig
        df['Valor'] = (
            df['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

        total_requests = len(df)
        pending_requests = len(df[df['Status'].isin(['Autorizado', 'Aguardando documentação'])])
        awaiting_payment_requests = len(df[df['Status'] == 'Pronto para pagamento'])
        paid_requests = len(df[df['Status'] == 'Pago'])
        total_paid_values = df[df['Status'] == 'Pago']['Valor'].sum()
        total_released_values = df[df['Status'].isin(['Pago', 'Pronto para pagamento'])]['Valor'].sum()

        stats_text = (
            f"Número total de solicitações: {total_requests}\n"
            f"Número de solicitações pendentes: {pending_requests}\n"
            f"Número de solicitações aguardando pagamento: {awaiting_payment_requests}\n"
            f"Número de solicitações pagas: {paid_requests}\n"
            f"Soma dos valores já pagos: R$ {total_paid_values:.2f}\n"
            f"Soma dos valores já liberados: R$ {total_released_values:.2f}\n"
        )

        label = tb.Label(self.graph_frame, text=stats_text, font=("Helvetica", 12), justify=LEFT)
        label.pack(pady=20, padx=20)

    def draw_barras(self, df):
        # Cria uma figura e exibe no graph_frame
        df['Valor'] = (
            df['Valor'].astype(str)
            .str.replace(',', '.')
            .str.extract(r'(\d+\.?\d*)')[0]
        )
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

        paid_data = df[df['Status'] == 'Pago'].copy()
        paid_data['Ultima Atualizacao'] = pd.to_datetime(
            paid_data['Ultima Atualizacao'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        paid_data = paid_data.dropna(subset=['Ultima Atualizacao'])

        fig, ax = plt.subplots(figsize=(6,4))
        if not paid_data.empty:
            group = paid_data.groupby(paid_data['Ultima Atualizacao'].dt.date)['Valor'].sum()
            group.plot(kind='bar', ax=ax)
            ax.set_title('Valores Pagos ao Longo do Tempo')
            ax.set_xlabel('Data')
            ax.set_ylabel('Valor Pago (R$)')
        else:
            ax.text(0.5, 0.5, 'Nenhum pagamento no período', ha='center', va='center')
            ax.set_title('Valores Pagos')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def draw_motivos(self, df):
        fig, ax = plt.subplots(figsize=(6,4))
        motivo_counts = df['Motivo da solicitação'].value_counts()
        if not motivo_counts.empty:
            motivo_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title('Distribuição por Motivo')
            ax.set_ylabel('')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado no período', ha='center', va='center')
            ax.set_title('Motivos')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def draw_agencias(self, df):
        fig, ax = plt.subplots(figsize=(6,4))
        agencia_counts = df['Qual a agência de fomento?'].value_counts()
        if not agencia_counts.empty:
            agencia_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title('Distribuição por Agência de Fomento')
            ax.set_ylabel('')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado no período', ha='center', va='center')
            ax.set_title('Agências de Fomento')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
