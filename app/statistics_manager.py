import os
import sys
from pathlib import Path
from datetime import datetime, date
import calendar
import tkinter as tk
from tkinter import PhotoImage, messagebox

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import mplcursors
    HAS_MPLCURSORS = True
except ImportError:
    HAS_MPLCURSORS = False

from login import BASE_DIR

ASSETS_PATH = BASE_DIR / "images" / "assets" / "graphview"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class RoundedButton(tk.Canvas):
    def __init__(
        self, parent, width=100, height=40, radius=10,
        bg_color="#2C3E50", fg_color="#ffffff",
        border_color="#000000", border_width=1,
        text="", font=None, command=None
    ):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0)
        self.radius = radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.border_width = border_width
        self.text_str = text
        self.font = font or ("Helvetica", 10, "bold")
        self.command = command

        self.bind("<Button-1>", self.on_click)
        self.draw_button()

    def draw_button(self):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        r = self.radius
        bw = self.border_width

        x1, y1 = bw, bw
        x2, y2 = w - bw, h - bw

        # Arcos para os cantos
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,
                        fill=self.bg_color, outline=self.bg_color)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,
                        fill=self.bg_color, outline=self.bg_color)

        # Retângulos centrais
        self.create_rectangle(x1+r, y1, x2-r, y2,
                              fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(x1, y1+r, x2, y2-r,
                              fill=self.bg_color, outline=self.bg_color)

        # Contorno (se necessário)
        if bw > 0:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,
                            style="arc", outline=self.border_color, width=bw)
            self.create_line(x1+r, y1, x2-r, y1, fill=self.border_color, width=bw)
            self.create_line(x1+r, y2, x2-r, y2, fill=self.border_color, width=bw)
            self.create_line(x1, y1+r, x1, y2-r, fill=self.border_color, width=bw)
            self.create_line(x2, y1+r, x2, y2-r, fill=self.border_color, width=bw)

        self.create_text(w//2, h//2, text=self.text_str,
                         fill=self.fg_color, font=self.font)

    def on_click(self, event):
        if self.command:
            self.command()
            
    def config_colors(self, bg_color=None, fg_color=None):
        if bg_color is not None:
            self.bg_color = bg_color
        if fg_color is not None:
            self.fg_color = fg_color
        self.draw_button()
        
class StatisticsManager:
    def __init__(self, app):
        self.app = app
        self.sheets_handler = self.app.sheets_handler
        self.stats_window = None
        self.main_canvas = None
        self.left_frame = None
        self.graph_frame = None

        self.current_period = "total"
        self.current_stat_type = "barras"

        self.period_buttons = {}
        self.type_buttons = {}
        self.info_labels = []

        # Variáveis para período personalizado
        self.custom_month_start = None
        self.custom_year_start = None
        self.custom_month_end = None
        self.custom_year_end = None

        self.current_figure = None
        self.period_label = None

        self.fixed_motives_order = [
            "Outros",
            "Visita técnica",
            "Trabalho de Campo",
            "Participação em eventos"
        ]

    def show_statistics(self):
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            return

        self.stats_window = tk.Toplevel(self.app.root)
        self.stats_window.title("Estatísticas - Layout Texto")

        w = 1000
        h = 760
        self.stats_window.geometry(f"{w}x{h}")
        self.stats_window.resizable(True, True)
        self._center_window(self.stats_window, w, h)

        self.stats_window.configure(bg="#2C3E50")

        self.main_canvas = tk.Canvas(self.stats_window, bg="#2C3E50",
                                     highlightthickness=0)
        self.main_canvas.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_canvas, bg="#2C3E50", width=250)
        self.left_frame.place(x=0, y=0, relheight=1.0)

        self.graph_frame = tk.Frame(self.main_canvas, bg="#D9D9D9")
        self.graph_frame.place(x=250, y=110, width=720, height=610)

        try:
            path_img = relative_to_assets("image_1.png")
            logo_img = PhotoImage(file=path_img)
            label_logo = tk.Label(self.main_canvas, image=logo_img, bg="#2C3E50")
            label_logo.image = logo_img
            label_logo.place(x=40, y=20)
        except Exception as e:
            print("Erro ao carregar image_1.png:", e)

        start_x = 280
        spacing_x = 140
        self.period_buttons["mes"] = self.create_period_button("Mês", "mes", x=start_x, y=20)
        start_x += spacing_x
        self.period_buttons["semestre"] = self.create_period_button("Semestre", "semestre", x=start_x, y=20)
        start_x += spacing_x
        self.period_buttons["ano"] = self.create_period_button("Ano", "ano", x=start_x, y=20)
        start_x += spacing_x
        self.period_buttons["total"] = self.create_period_button("Total", "total", x=start_x, y=20)
        start_x += spacing_x
        self.period_buttons["custom"] = self.create_period_button("Personalizado", "custom", x=start_x, y=20)

        self.period_label = tk.Label(
            self.main_canvas, text="Visualizando: --",
            bg="#2C3E50", fg="#fff", font=("Helvetica", 11, "bold")
        )
        self.period_label.place(x=280, y=65)

        self.type_buttons["barras"] = self.create_type_button("Barras", "barras", x=20, y=100)
        self.type_buttons["motivos"] = self.create_type_button("Motivos", "motivos", x=20, y=150)
        self.type_buttons["agencias"] = self.create_type_button("Agências", "agencias", x=20, y=200)
        self.type_buttons["acumulado"] = self.create_type_button("Acumulado", "acumulado", x=20, y=250)

        info_frame = tk.Frame(self.left_frame, bg="#2C3E50")
        info_frame.place(x=20, y=330, width=200, height=250)
        info_keys = [
            "Total Solicitações",
            "Pendentes",
            "Aguardando Pagto",
            "Pagas",
            "Valor Pago (R$)",
            "Valor Liberado (R$)"
        ]
        self.info_labels.clear()
        for i, key in enumerate(info_keys):
            lbl_k = tk.Label(info_frame, text=key, bg="#2C3E50", fg="#000",
                             width=15, anchor="e")
            lbl_k.grid(row=i, column=0, sticky="e", padx=5, pady=2)
            lbl_v = tk.Label(info_frame, text="0", bg="#2C3E50", fg="#000",
                             width=10, anchor="w")
            lbl_v.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.info_labels.append((key, lbl_v))

        self.create_rounded_button(
            parent=self.left_frame,
            text="Voltar",
            x=20, y=650, w=180, h=40,
            radius=10,
            bg_color="#D9D9D9", fg_color="#000",
            border_color="#000", border_width=1,
            command=self.close_window
        )

        self.set_period("total")
        self.set_stat_type("barras")
        self.redraw_chart()

    def _center_window(self, window, w, h):
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = int((ws - w)//2)
        y = int((hs - h)//2)
        window.geometry(f"{w}x{h}+{x}+{y}")

    def create_rounded_button(self, parent, text, x, y,
                              w=100, h=40, radius=10,
                              bg_color="#2C3E50", fg_color="#ffffff",
                              border_color="#000000", border_width=1,
                              command=None):
        btn = RoundedButton(
            parent, width=w, height=h, radius=radius,
            bg_color=bg_color, fg_color=fg_color,
            border_color=border_color, border_width=border_width,
            text=text, font=("Helvetica", 10, "bold"),
            command=command
        )
        btn.place(x=x, y=y)
        return btn

    def create_period_button(self, label, period, x, y):
        def cmd():
            if period == "custom":
                self.ask_custom_period()
            else:
                self.set_period(period)
        btn = RoundedButton(
            self.main_canvas, width=110, height=40, radius=10,
            bg_color="#2C3E50", fg_color="#fff",
            border_color="#000000", border_width=1,
            text=label, font=("Helvetica", 10, "bold"),
            command=cmd
        )
        btn.place(x=x, y=y)
        return btn

    def create_type_button(self, label, stype, x, y):
        def cmd():
            self.set_stat_type(stype)
        btn = RoundedButton(
            self.left_frame, width=180, height=40, radius=10,
            bg_color="#ffffff", fg_color="#000000",
            border_color="#000000", border_width=1,
            text=label, font=("Helvetica", 10, "bold"),
            command=cmd
        )
        btn.place(x=x, y=y)
        return btn

    def set_period(self, period):
        self.current_period = period
        for p, rb in self.period_buttons.items():
            rb.config_colors(bg_color="#2C3E50", fg_color="#fff")
        if period in self.period_buttons:
            self.period_buttons[period].config_colors(bg_color="#1ABC9C", fg_color="#fff")

        self.update_period_label()
        self.redraw_chart()

    def set_stat_type(self, stype):
        self.current_stat_type = stype
        for t, rb in self.type_buttons.items():
            rb.config_colors(bg_color="#ffffff", fg_color="#000000")
        if stype in self.type_buttons:
            self.type_buttons[stype].config_colors(bg_color="#2C3E50", fg_color="#fff")

        self.redraw_chart()

    def close_window(self):
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.destroy()
            self.stats_window = None

    def update_period_label(self):
        if not self.period_label:
            return
        if self.current_period == "mes":
            text = "Visualizando: Mês atual (por semanas, Status=Pago)"
        elif self.current_period == "semestre":
            now = date.today()
            sem = 1 if now.month <= 6 else 2
            text = f"Visualizando: {sem}º Semestre de {now.year} (mes a mes, pagos)"
        elif self.current_period == "ano":
            text = f"Visualizando: Ano {date.today().year} (mes a mes, pagos)"
        elif self.current_period == "custom":
            try:
                ms = int(self.custom_month_start.get())
                ys = int(self.custom_year_start.get())
                me = int(self.custom_month_end.get())
                ye = int(self.custom_year_end.get())
                text = f"Visualizando: {ms:02d}/{ys} a {me:02d}/{ye} (pagos)"
            except:
                text = "Visualizando: Custom (erro, pagos)"
        else:
            text = "Visualizando: Todos (agrupado por semestre, somente pagos)"
        self.period_label.config(text=text)

    def ask_custom_period(self):
        custom_win = tk.Toplevel(self.stats_window)
        custom_win.title("Período Personalizado")
        cw, ch = 300, 220
        custom_win.geometry(f"{cw}x{ch}")
        self._center_window(custom_win, cw, ch)
        custom_win.config(bg="#ECF0F1")

        tk.Label(custom_win, text="Mês/Ano INÍCIO:", bg="#ECF0F1").pack(pady=5)
        months = [str(i).zfill(2) for i in range(1, 13)]
        years = [str(y) for y in range(2020, 2035)]

        self.custom_month_start = tk.StringVar(value="01")
        self.custom_year_start = tk.StringVar(value="2023")
        today = date.today()
        self.custom_month_end = tk.StringVar(value=str(today.month).zfill(2))
        self.custom_year_end = tk.StringVar(value=str(today.year))

        frame_start = tk.Frame(custom_win, bg="#ECF0F1")
        frame_start.pack()
        om1 = tk.OptionMenu(frame_start, self.custom_month_start, *months)
        om1.pack(side="left", padx=5)
        om2 = tk.OptionMenu(frame_start, self.custom_year_start, *years)
        om2.pack(side="left", padx=5)

        tk.Label(custom_win, text="Mês/Ano FIM:", bg="#ECF0F1").pack(pady=5)
        frame_end = tk.Frame(custom_win, bg="#ECF0F1")
        frame_end.pack()
        om3 = tk.OptionMenu(frame_end, self.custom_month_end, *months)
        om3.pack(side="left", padx=5)
        om4 = tk.OptionMenu(frame_end, self.custom_year_end, *years)
        om4.pack(side="left", padx=5)

        tk.Label(custom_win, text="Granularidade:", bg="#ECF0F1").pack(pady=5)
        self.custom_granularity = tk.StringVar(value="mensal")
        granularity_options = ["mensal", "semestral", "anual"]
        frame_granularity = tk.Frame(custom_win, bg="#ECF0F1")
        frame_granularity.pack()
        om5 = tk.OptionMenu(frame_granularity, self.custom_granularity, *granularity_options)
        om5.pack(side="left", padx=5)

        def apply_custom():
            self.set_period("custom")
            custom_win.destroy()

        tk.Button(custom_win, text="Aplicar",
                  bg="#1ABC9C", fg="#fff",
                  font=("Helvetica", 10, "bold"), bd=0,
                  command=apply_custom).pack(pady=10)

    def _apply_period_filter(self, df):
        now = pd.Timestamp.now()
        df = df.copy()
        if df.empty:
            return df

        if self.current_period == "mes":
            year = now.year
            month = now.month
            start_date = pd.Timestamp(year, month, 1)
            days_in_month = calendar.monthrange(year, month)[1]
            end_date = pd.Timestamp(year, month, days_in_month, 23, 59, 59)
            df = df[(df['Ultima Atualizacao'] >= start_date) & (df['Ultima Atualizacao'] <= end_date)].copy()
            if "SemanaMes" not in df.columns:
                df["SemanaMes"] = df["Ultima Atualizacao"].apply(lambda d: ((d.day - 1) // 7 + 1) if pd.notnull(d) else 0)
            else:
                df["SemanaMes"] = df["SemanaMes"].fillna(0).astype(int)
            return df

        elif self.current_period == "semestre":
            year = now.year
            if now.month <= 6:
                start_date = pd.Timestamp(year, 1, 1)
                end_date = pd.Timestamp(year, 6, 30, 23, 59, 59)
            else:
                start_date = pd.Timestamp(year, 7, 1)
                end_date = pd.Timestamp(year, 12, 31, 23, 59, 59)
            df = df[(df['Ultima Atualizacao'] >= start_date) & (df['Ultima Atualizacao'] <= end_date)].copy()
            df["MesAbrev"] = df["Ultima Atualizacao"].dt.strftime("%b").map(self._translate_month)
            return df

        elif self.current_period == "ano":
            year = now.year
            start_date = pd.Timestamp(year, 1, 1)
            end_date = pd.Timestamp(year, 12, 31, 23, 59, 59)
            df = df[(df['Ultima Atualizacao'] >= start_date) & (df['Ultima Atualizacao'] <= end_date)].copy()
            df["MesAbrev"] = df["Ultima Atualizacao"].dt.strftime("%b").map(self._translate_month)
            return df

        elif self.current_period == "custom":
            try:
                ms = int(self.custom_month_start.get())
                ys = int(self.custom_year_start.get())
                me = int(self.custom_month_end.get())
                ye = int(self.custom_year_end.get())
                start_date = pd.Timestamp(ys, ms, 1, 0, 0, 0)
                days_in_end = calendar.monthrange(ye, me)[1]
                end_date = pd.Timestamp(ye, me, days_in_end, 23, 59, 59)
                df = df[(df['Ultima Atualizacao'] >= start_date) & (df['Ultima Atualizacao'] <= end_date)].copy()
                granularity = self.custom_granularity.get()
                if granularity == "mensal":
                    df["Periodo"] = df["Ultima Atualizacao"].dt.to_period("M")
                elif granularity == "semestral":
                    df["Periodo"] = df["Ultima Atualizacao"].dt.to_period("6M")
                elif granularity == "anual":
                    df["Periodo"] = df["Ultima Atualizacao"].dt.to_period("Y")
            except:
                messagebox.showwarning("Aviso", "Datas inválidas, exibindo tudo.")
            return df
        else:
            def year_sem(dt):
                y = dt.year
                s = 1 if dt.month <= 6 else 2
                return (y, s)
            df["YearSem"] = df["Ultima Atualizacao"].apply(year_sem)
            return df

    def _translate_month(self, month_abbr):
        translations = {
            "Jan": "Jan", "Feb": "Fev", "Mar": "Mar", "Apr": "Abr", "May": "Mai", "Jun": "Jun",
            "Jul": "Jul", "Aug": "Ago", "Sep": "Set", "Oct": "Out", "Nov": "Nov", "Dec": "Dez"
        }
        return translations.get(month_abbr, month_abbr)

    def redraw_chart(self):
        if not self.stats_window or not self.stats_window.winfo_exists():
            return

        df = self.sheets_handler.load_data()
        df['Ultima Atualizacao'] = pd.to_datetime(
            df['Ultima Atualizacao'],
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )

        df = df[df['Status'] == 'Pago'].copy()
        df = self._apply_period_filter(df)

        if self.current_figure:
            plt.close(self.current_figure)
            self.current_figure = None

        for w in self.graph_frame.winfo_children():
            w.destroy()

        self.update_info_box(df)

        if self.current_stat_type == "barras":
            self.draw_barras(df)
        elif self.current_stat_type == "motivos":
            self.draw_motivos_side_by_side(df)
        elif self.current_stat_type == "acumulado":
            self.draw_acumulado(df)
        else:
            self.draw_agencias(df)

    def update_info_box(self, df):
        if df.empty:
            total_requests = 0
            pending_requests = 0
            awaiting_payment_requests = 0
            paid_requests = 0
            total_paid_values = 0.0
            total_released_values = 0.0
        else:
            total_requests = len(df)
            pending_requests = 0
            awaiting_payment_requests = 0
            paid_requests = len(df)
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            total_paid_values = df['Valor'].sum()
            total_released_values = df['Valor'].sum()

        info_map = {
            "Total Solicitações": f"{total_requests}",
            "Pendentes": f"{pending_requests}",
            "Aguardando Pagto": f"{awaiting_payment_requests}",
            "Pagas": f"{paid_requests}",
            "Valor Pago (R$)": f"{total_paid_values:.2f}",
            "Valor Liberado (R$)": f"{total_released_values:.2f}"
        }
        for (key, lbl_val) in self.info_labels:
            lbl_val.config(text=info_map.get(key, "0"))

    def draw_barras(self, df):
        import matplotlib.cm as cm
        self.current_figure, ax = plt.subplots(figsize=(7, 5))
        self.current_figure.set_facecolor("#D9D9D9")
        ax.set_facecolor("#D9D9D9")
        ax.set_ylabel("Valor (R$)")

        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

        if df.empty:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
            ax.axis('off')
        else:
            if self.current_period == "mes":
                if "SemanaMes" not in df.columns:
                    ax.text(0.5, 0.5, "Sem 'SemanaMes'", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby(["SemanaMes", "Motivo da solicitação"])["Valor"].sum().unstack(fill_value=0)
                    weeks_index = [1, 2, 3, 4, 5]
                    pivot = pivot.reindex(weeks_index, fill_value=0)
                    x = np.arange(len(weeks_index))
                    bottom = np.zeros(len(x))
                    motives = pivot.columns
                    color_map = cm.get_cmap('Blues', len(motives) + 1)
                    for i, motive in enumerate(motives[::-1]):
                        vals = pivot[motive].values
                        c = color_map(float(i + 1) / len(motives))
                        ax.bar(x, vals, bottom=bottom, color=c, label=motive)
                        bottom += vals
                    for i, val in enumerate(bottom):
                        if val > 0:
                            ax.text(x[i], val * 1.01, f"{val:.2f}",
                                    ha='center', va='bottom', fontsize=8, color='black')
                    ax.set_xticks(x)
                    ax.set_xticklabels([f"Sem{w}" for w in weeks_index])
                    ax.legend(fontsize=8)
                    max_val = bottom.max()
                    ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

            elif self.current_period == "semestre":
                if "MesAbrev" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col MesAbrev", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby(["MesAbrev", "Motivo da solicitação"])["Valor"].sum().unstack(fill_value=0)
                    if pivot.empty:
                        ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
                        ax.axis('off')
                    else:
                        now = date.today()
                        if now.month <= 6:
                            semester_months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
                        else:
                            semester_months = ["Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                        pivot = pivot.reindex(semester_months, fill_value=0)
                        x = np.arange(len(semester_months))
                        bottom = np.zeros(len(x))
                        motives = pivot.columns
                        color_map = cm.get_cmap('Blues', len(motives) + 1)
                        for i, motive in enumerate(motives[::-1]):
                            vals = pivot[motive].values
                            c = color_map(float(i + 1) / len(motives))
                            ax.bar(x, vals, bottom=bottom, color=c, label=motive)
                            bottom += vals
                        for i, val in enumerate(bottom):
                            if val > 0:
                                ax.text(i, val * 1.01, f"{val:.2f}",
                                        ha='center', va='bottom', fontsize=8, color='black')
                        ax.set_xticks(x)
                        ax.set_xticklabels(semester_months, rotation=45, ha='right')
                        ax.legend(fontsize=8)
                        max_val = bottom.max()
                        ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

            elif self.current_period == "ano":
                if "MesAbrev" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col MesAbrev", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby(["MesAbrev", "Motivo da solicitação"])["Valor"].sum().unstack(fill_value=0)
                    if pivot.empty:
                        ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
                        ax.axis('off')
                    else:
                        all_months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                        pivot = pivot.reindex(all_months, fill_value=0)
                        x = np.arange(len(all_months))
                        bottom = np.zeros(len(x))
                        motives = pivot.columns
                        color_map = cm.get_cmap('Blues', len(motives) + 1)
                        for i, motive in enumerate(motives[::-1]):
                            vals = pivot[motive].values
                            c = color_map(float(i + 1) / len(motives))
                            ax.bar(x, vals, bottom=bottom, color=c, label=motive)
                            bottom += vals
                        for i, val in enumerate(bottom):
                            if val > 0:
                                ax.text(i, val * 1.01, f"{val:.2f}",
                                        ha='center', va='bottom', fontsize=8, color='black')
                        ax.set_xticks(x)
                        ax.set_xticklabels(all_months, rotation=45, ha='right')
                        ax.legend(fontsize=8)
                        max_val = bottom.max()
                        ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

            elif self.current_period == "custom":
                if "Periodo" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col Periodo", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby(["Periodo", "Motivo da solicitação"])["Valor"].sum().unstack(fill_value=0)
                    if pivot.empty:
                        ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
                        ax.axis('off')
                    else:
                        periods = pivot.index
                        x = np.arange(len(periods))
                        bottom = np.zeros(len(x))
                        motives = pivot.columns
                        color_map = cm.get_cmap('Blues', len(motives) + 1)
                        for i, motive in enumerate(motives[::-1]):
                            vals = pivot[motive].values
                            c = color_map(float(i + 1) / len(motives))
                            ax.bar(x, vals, bottom=bottom, color=c, label=motive)
                            bottom += vals
                        for i, val in enumerate(bottom):
                            if val > 0:
                                ax.text(i, val * 1.01, f"{val:.2f}",
                                        ha='center', va='bottom', fontsize=8, color='black')
                        ax.set_xticks(x)
                        ax.set_xticklabels([str(p) for p in periods], rotation=45, ha='right')
                        ax.legend(fontsize=8)
                        max_val = bottom.max()
                        ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

            else:
                if "YearSem" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col YearSem", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby(["YearSem", "Motivo da solicitação"])["Valor"].sum().unstack(fill_value=0)
                    if pivot.empty:
                        ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
                        ax.axis('off')
                    else:
                        sorted_idx = sorted(pivot.index, key=lambda t: (t[0], t[1]))
                        pivot = pivot.reindex(sorted_idx)
                        x = np.arange(len(pivot.index))
                        bottom = np.zeros(len(x))
                        motives = pivot.columns
                        color_map = cm.get_cmap('Blues', len(motives) + 1)
                        for i, motive in enumerate(motives[::-1]):
                            vals = pivot[motive].values
                            c = color_map(float(i + 1) / len(motives))
                            ax.bar(x, vals, bottom=bottom, color=c, label=motive)
                            bottom += vals
                        for i, val in enumerate(bottom):
                            if val > 0:
                                ax.text(i, val * 1.01, f"{val:.2f}",
                                        ha='center', va='bottom', fontsize=8, color='black')
                        labels = [f"{y}-S{s}" for (y, s) in pivot.index]
                        ax.set_xticks(x)
                        ax.set_xticklabels(labels, rotation=45, ha='right')
                        ax.legend(fontsize=8)
                        max_val = bottom.max()
                        ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

        canvas = FigureCanvasTkAgg(self.current_figure, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_motivos_side_by_side(self, df):
        import matplotlib.cm as cm
        self.current_figure, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(8, 5))
        self.current_figure.set_facecolor("#D9D9D9")
        ax_bar.set_facecolor("#D9D9D9")
        ax_pie.set_facecolor("#D9D9D9")
    
        ax_bar.set_ylabel("Valor (R$)")
    
        if df.empty:
            ax_bar.text(0.5, 0.5, "Sem dados", ha='center', va='center')
            ax_bar.axis('off')
            ax_pie.text(0.5, 0.5, "Sem dados", ha='center', va='center')
            ax_pie.axis('off')
        else:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            group = df.groupby('Motivo da solicitação')['Valor'].sum()
            group_fixed = group.reindex(self.fixed_motives_order, fill_value=0)
            total_sum = group_fixed.sum()
    
            if total_sum <= 0:
                ax_bar.text(0.5, 0.5, "Sem dados (pagos)", ha='center', va='center')
                ax_bar.axis('off')
                ax_pie.text(0.5, 0.5, "Sem dados (pagos)", ha='center', va='center')
                ax_pie.axis('off')
            else:
                n = len(self.fixed_motives_order)
                color_map = cm.get_cmap('Blues', n + 1)
                x = np.arange(n)
                for i, motive in enumerate(self.fixed_motives_order):
                    val = group_fixed[motive]
                    c = color_map(float(i + 1) / n)
                    ax_bar.bar(x[i], val, color=c, width=0.6)
                    if val > 0:
                        ax_bar.text(x[i], val * 1.01, f"{val:.2f}",
                                    ha='center', va='bottom', fontsize=8)
                ax_bar.set_xticks(x)
                ax_bar.set_xticklabels(self.fixed_motives_order, rotation=45, ha='right')
                ax_bar.set_title("Motivos: Barras (Pagos)")
                maxv = group_fixed.max()
                ax_bar.set_ylim(0, maxv * 1.2 if maxv > 0 else 1)
    
                values = group_fixed.values
                colors = [color_map(float(i + 1) / n) for i in range(n)]
                wedges, _, _ = ax_pie.pie(values, labels=None, colors=colors, autopct='%1.1f%%')
                ax_pie.set_title("Motivos: Pizza (Pagos)")
                ax_pie.legend(wedges, self.fixed_motives_order, fontsize=8,
                              loc='lower center', bbox_to_anchor=(0.5, -0.15),
                              ncol=2)
    
        self.current_figure.tight_layout()
        canvas = FigureCanvasTkAgg(self.current_figure, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def draw_acumulado(self, df):
        self.current_figure, ax = plt.subplots(figsize=(7, 5))
        self.current_figure.set_facecolor("#D9D9D9")
        ax.set_facecolor("#D9D9D9")
        ax.set_ylabel("Valor Acumulado (R$)")
    
        if df.empty:
            ax.text(0.5, 0.5, "Sem dados (pagos)", ha='center', va='center')
            ax.axis('off')
        else:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
    
            if self.current_period == "mes":
                if "SemanaMes" not in df.columns:
                    ax.text(0.5, 0.5, "Sem 'SemanaMes'", ha='center', va='center')
                    ax.axis('off')
                else:
                    group = df.groupby("SemanaMes")["Valor"].sum()
                    weeks_index = [1, 2, 3, 4, 5]
                    group = group.reindex(weeks_index, fill_value=0)
                    cumvals = group.cumsum()
                    x = np.arange(1, 6)
                    ax.plot(x, cumvals, color="navy", marker="o", linewidth=2)
                    for i, val in enumerate(cumvals):
                        if val > 0:
                            ax.text(x[i], val, f"{val:.2f}",
                                    ha='left', va='bottom', color='black', fontsize=9)
                    ax.set_xticks(x)
                    ax.set_xticklabels([f"Sem{w}" for w in weeks_index])
                    ax.set_title("Acumulado (Mês)")
    
            elif self.current_period == "semestre":
                if "MesAbrev" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col MesAbrev", ha='center', va='center')
                    ax.axis('off')
                else:
                    group = df.groupby("MesAbrev")["Valor"].sum()
                    now = date.today()
                    if now.month <= 6:
                        semester_months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
                    else:
                        semester_months = ["Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                    group = group.reindex(semester_months, fill_value=0)
                    cumvals = group.cumsum()
                    x = np.arange(len(semester_months))
                    ax.plot(x, cumvals, color="navy", marker="o", linewidth=2)
                    for i, val in enumerate(cumvals):
                        if val > 0:
                            ax.text(x[i], val, f"{val:.2f}",
                                    ha='left', va='bottom', color='black', fontsize=9)
                    ax.set_xticks(x)
                    ax.set_xticklabels(semester_months, rotation=45, ha='right')
                    ax.set_title("Acumulado (Semestre)")
    
            elif self.current_period == "ano":
                if "MesAbrev" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col MesAbrev", ha='center', va='center')
                    ax.axis('off')
                else:
                    group = df.groupby("MesAbrev")["Valor"].sum()
                    all_months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                    group = group.reindex(all_months, fill_value=0)
                    cumvals = group.cumsum()
                    x = np.arange(12)
                    ax.plot(x, cumvals, color="navy", marker="o", linewidth=2)
                    for i, val in enumerate(cumvals):
                        if val > 0:
                            ax.text(x[i], val, f"{val:.2f}",
                                    ha='left', va='bottom', color='black', fontsize=9)
                    ax.set_xticks(x)
                    ax.set_xticklabels(all_months, rotation=45, ha='right')
                    ax.set_title("Acumulado (Ano)")
    
            elif self.current_period == "custom":
                if "Periodo" not in df.columns:
                    ax.text(0.5, 0.5, "Sem col Periodo", ha='center', va='center')
                    ax.axis('off')
                else:
                    pivot = df.groupby("Periodo")["Valor"].sum().reindex(df["Periodo"].unique(), fill_value=0)
                    cumvals = pivot.cumsum()
                    x = np.arange(len(pivot.index))
                    ax.plot(x, cumvals, color="navy", marker="o", linewidth=2)
                    for i, val in enumerate(cumvals):
                        if val > 0:
                            ax.text(x[i], val, f"{val:.2f}",
                                    ha='left', va='bottom', color='black', fontsize=9)
                    ax.set_xticks(x)
                    ax.set_xticklabels([str(p) for p in pivot.index], rotation=45, ha='right')
                    ax.set_title("Acumulado (Personalizado)")
    
            else:
                df = df.sort_values(by=["Ultima Atualizacao"])
                df['Acumulado'] = df['Valor'].cumsum()
    
                times = df['Ultima Atualizacao']
                vals = df['Acumulado']
    
                if len(times) == 0:
                    ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
                    ax.axis('off')
                else:
                    ax.plot(times, vals, color="navy", marker="o", linewidth=2)
                    max_val = vals.iloc[-1]
                    max_time = times.iloc[-1]
                    ax.text(max_time, max_val, f"{max_val:.2f}",
                            ha='left', va='bottom', color='black', fontsize=9)
                    ax.set_title("Valor Acumulado (Pagos)")
    
        canvas = FigureCanvasTkAgg(self.current_figure, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def draw_agencias(self, df):
        import matplotlib.cm as cm
        self.current_figure, ax = plt.subplots(figsize=(7, 5))
        self.current_figure.set_facecolor("#D9D9D9")
        ax.set_facecolor("#D9D9D9")
    
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
        agencias = df['Qual a agência de fomento?'].value_counts()
        total_a = agencias.sum()
        if total_a <= 0:
            ax.text(0.5, 0.5, "Nenhum dado de Agências", ha='center', va='center')
            ax.axis('off')
        else:
            n = len(agencias)
            color_map = cm.get_cmap('Blues', n + 1)
            colors = [color_map(float(i + 1) / n) for i in range(n)]
            wedges, _, _ = ax.pie(agencias.values, labels=None,
                                  colors=colors, autopct='%1.1f%%')
            ax.set_title("Agências")
            ax.legend(wedges, agencias.index, loc='best', fontsize=8)
    
        canvas = FigureCanvasTkAgg(self.current_figure, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
