import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from config import *


class ProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_LIGHT_PURPLE)
        self.controller = controller

        # Titlu Pagină
        tk.Label(self, text="Raport de Progres și Statistici", font=FONT_TITLE,
                 bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(pady=(20, 10))

        # Container principal Scrollabil
        container = tk.Frame(self, bg=C_LIGHT_PURPLE)
        container.pack(fill="both", expand=True, padx=30, pady=10)

        canvas_scroll = tk.Canvas(container, bg=C_LIGHT_PURPLE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas_scroll.yview)
        self.scrollable_content = tk.Frame(canvas_scroll, bg=C_LIGHT_PURPLE)

        self.scrollable_content.bind("<Configure>",
                                     lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_window = canvas_scroll.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.itemconfig(canvas_window, width=e.width))
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Zona 1: Casete KPI (Statistici Rapide)
        self.kpi_frame = tk.Frame(self.scrollable_content, bg=C_LIGHT_PURPLE)
        self.kpi_frame.pack(fill="x", pady=(0, 20))

        # Zona 2: Grid-ul pentru Grafice
        self.charts_frame = tk.Frame(self.scrollable_content, bg=C_LIGHT_PURPLE)
        self.charts_frame.pack(fill="both", expand=True, pady=10)
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.columnconfigure(1, weight=1)

    def refresh_statistics(self):
        # 1. Curățăm elementele vechi de pe ecran
        for w in self.kpi_frame.winfo_children(): w.destroy()
        for w in self.charts_frame.winfo_children(): w.destroy()

        user = self.controller.auth_service.current_user
        if not user: return

        # 2. Preluăm datele calculate din backend
        stats = self.controller.planner_service.get_statistics_data(user['id'])

        # --- RANDARE CASETE KPI ---
        top_mat = max(stats["discipline_time"], key=stats["discipline_time"].get) if stats.get(
            "discipline_time") else "Niciuna"

        # LOGICĂ NOUĂ: Afișăm în Minute dacă e sub 60, altfel în Ore
        # Folosim .get() cu fallback la 'total_ore' * 60 în caz că backend-ul încă returnează ore
        total_m = stats.get('total_minute', stats.get('total_ore', 0) * 60)
        display_timp = f"{total_m:.1f} Min" if total_m < 60 else f"{total_m / 60:.1f} Ore"

        self.create_kpi_card(self.kpi_frame, "⏱️ TOTAL STUDIAT", display_timp).grid(row=0, column=0, padx=10,
                                                                                    sticky="ew")
        self.create_kpi_card(self.kpi_frame, "👑 TOP MATERIE", top_mat).grid(row=0, column=1, padx=10, sticky="ew")

        # Siguranță pentru cheia deadlines_status
        teme_fin = stats.get('deadlines_status', {}).get('Finalizate', 0)
        self.create_kpi_card(self.kpi_frame, "✅ TEME FINALIZATE", f"{teme_fin} Sarcini").grid(row=0, column=2, padx=10,
                                                                                              sticky="ew")

        self.kpi_frame.columnconfigure((0, 1, 2), weight=1)

        # --- GRAFIC 1: TIMP PE MATERII (BAR CHART) ---
        fig1, ax1 = plt.subplots(figsize=(4, 3), facecolor='#fbf9ff')
        if stats.get("discipline_time"):
            materii = list(stats["discipline_time"].keys())
            minute = list(stats["discipline_time"].values())  # Acum lucrăm cu minute!
            ax1.bar(materii, minute, color='#4b0082')
            ax1.set_ylabel('Minute', fontsize=9, fontweight='bold', color='#4b0082')
            ax1.tick_params(axis='x', rotation=15, labelsize=8)
        else:
            ax1.text(0.5, 0.5, 'Nu ai înregistrat\nsesiuni de studiu', ha='center', va='center', color="#777")
        ax1.set_title("Timp Studiu / Materie", fontsize=11, fontweight='bold', color='#4b0082')
        fig1.tight_layout()

        # --- GRAFIC 2: STATUS DEADLINES (PIE CHART) ---
        fig2, ax2 = plt.subplots(figsize=(4, 3), facecolor='#fbf9ff')
        status_data = stats.get("deadlines_status", {})
        if sum(status_data.values()) > 0:
            labels = [k for k, v in status_data.items() if v > 0]
            values = [v for k, v in status_data.items() if v > 0]  # FIX-ul corect aplicat aici
            culori = {'Urmează': '#a8c8f5', 'Finalizate': '#a8f5b8', 'Depășite': '#f5a8c8'}
            ax2.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                    colors=[culori.get(l, '#ccc') for l in labels], textprops={'fontsize': 9, 'weight': 'bold'})
        else:
            ax2.text(0.5, 0.5, 'Nu ai deadline-uri', ha='center', va='center', color="#777")
        ax2.set_title("Status Deadlines", fontsize=11, fontweight='bold', color='#4b0082')
        fig2.tight_layout()

        # --- GRAFIC 3: EVOLUȚIA ÎN ULTIMELE 7 ZILE (LINE CHART) ---
        fig3, ax3 = plt.subplots(figsize=(8, 2.5), facecolor='#fbf9ff')
        zile_ultimele = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(6, -1, -1)]
        minute_zile = [stats.get("daily_time", {}).get(zi, 0) for zi in zile_ultimele]
        zile_etichete = [zi[:5] for zi in zile_ultimele]

        ax3.plot(zile_etichete, minute_zile, marker='o', linewidth=2, color='#4b0082', markerfacecolor='#a8f5b8',
                 markersize=8)
        ax3.set_ylabel('Minute', fontsize=9, fontweight='bold', color='#4b0082')
        ax3.set_title("Evoluția studiului în ultimele 7 zile", fontsize=11, fontweight='bold', color='#4b0082')
        ax3.grid(True, linestyle='--', alpha=0.4)
        fig3.tight_layout()

        # --- INTEGRAREA GRAFICELOR ÎN INTERFAȚĂ ---
        canvas1 = FigureCanvasTkAgg(fig1, master=self.charts_frame)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        canvas2 = FigureCanvasTkAgg(fig2, master=self.charts_frame)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        canvas3 = FigureCanvasTkAgg(fig3, master=self.charts_frame)
        canvas3.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Foarte important pentru a nu încărca memoria (Memory Leak)
        plt.close('all')

    def create_kpi_card(self, parent, title, value):
        card = tk.Frame(parent, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2, padx=15, pady=15)
        tk.Label(card, text=title, font=("Arial", 9, "bold"), bg=C_WHITE, fg="#777").pack(anchor="w")
        tk.Label(card, text=value, font=("Georgia", 16, "bold"), bg=C_WHITE, fg=C_DARK_PURPLE).pack(anchor="w",
                                                                                                    pady=(5, 0))
        return card