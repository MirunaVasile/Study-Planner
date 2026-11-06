# study_sessions_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
from config import *


class TimerWindow(tk.Toplevel):
    def __init__(self, parent, controller, disc_map, on_close_callback, resume_info=None):
        super().__init__(parent)
        self.controller = controller
        self.disc_map = disc_map
        self.on_close_callback = on_close_callback
        self.resume_info = resume_info

        self.title("Sesiune de Studiu")
        self.geometry("500x570")
        self.configure(bg=C_LIGHT_PURPLE)
        self.grab_set()

        self.running = False
        self.mode = "stopwatch"
        self.time_seconds = 0
        self.target_seconds = 0
        self.elapsed_today = 0
        self.disciplina_aleasa = None

        self.frame_form = tk.Frame(self, bg=C_LIGHT_PURPLE)
        self.frame_timer = tk.Frame(self, bg=C_LIGHT_PURPLE)

        self.setup_form()
        self.setup_timer()

        if self.resume_info:
            self.disciplina_aleasa = self.resume_info['disc_id']
            self.target_seconds = self.resume_info['durata_tinta']
            if self.target_seconds > 0:
                self.mode = "countdown"
                self.time_seconds = self.target_seconds - self.resume_info['total_secunde']
            else:
                self.mode = "stopwatch"
                self.time_seconds = self.resume_info['total_secunde']
            self.lbl_sess_materie.config(text=self.resume_info['materie'])
            self.lbl_sess_notite.config(text=self.resume_info['notite'])
            self.update_timer_display()
            self.frame_timer.pack(fill="both", expand=True)
            self.running = True
            self.tick()
        else:
            self.frame_form.pack(fill="both", expand=True)

    def setup_form(self):
        tk.Label(self.frame_form, text="Setează Sesiunea", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(
            pady=(30, 20))
        card = tk.Frame(self.frame_form, bg=C_PANEL_BG, padx=30, pady=30, highlightbackground=C_WHITE,
                        highlightthickness=1)
        card.pack(fill="x", padx=40)

        tk.Label(card, text="Alege Materia:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).pack(anchor="w")
        self.combo_disc = ttk.Combobox(card, values=list(self.disc_map.keys()), state="readonly", font=FONT_NORMAL)
        if self.disc_map: self.combo_disc.set(list(self.disc_map.keys())[0])
        self.combo_disc.pack(fill="x", pady=(5, 15))

        tk.Label(card, text="Notițe:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).pack(anchor="w")
        self.entry_notite = tk.Entry(card, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_notite.pack(fill="x", ipady=5, pady=(5, 15))

        tk.Label(card, text="Durată (minute):", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).pack(anchor="w")
        time_f = tk.Frame(card, bg=C_PANEL_BG)
        time_f.pack(fill="x", pady=5)

        self.spin_timp = ttk.Spinbox(time_f, from_=1, to=300, width=5, font=FONT_NORMAL)
        self.spin_timp.set(30)
        self.spin_timp.pack(side="left")

        self.var_nu_stiu = tk.BooleanVar()
        tk.Checkbutton(time_f, text="Nu știu", variable=self.var_nu_stiu, bg=C_PANEL_BG, command=self.toggle_spin).pack(
            side="left", padx=10)

        sugestii = self.controller.planner_service.get_sugestii_timp()
        sugestii_frame = tk.Frame(card, bg=C_PANEL_BG)
        sugestii_frame.pack(fill="x", pady=(15, 0))

        tk.Label(sugestii_frame, text="Sugestii:", bg=C_PANEL_BG, fg="#777", font=("Arial", 9)).pack(side="left")

        for val in sugestii:
            btn = tk.Button(sugestii_frame, text=f"{val}m", bg="#a8c8f5", fg=C_DARK_PURPLE, relief="flat",
                            cursor="hand2",
                            font=("Arial", 9, "bold"),
                            command=lambda v=val: self.spin_timp.set(v))
            btn.pack(side="left", padx=5)

        tk.Button(self.frame_form, text="▶ Începe", font=("Georgia", 14, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE,
                  relief="flat", command=self.start_session).pack(pady=30, ipady=10, ipadx=30)

    def toggle_spin(self):
        self.spin_timp.config(state="disabled" if self.var_nu_stiu.get() else "normal")

    def start_session(self):
        self.disciplina_aleasa = self.disc_map[self.combo_disc.get()]
        if self.var_nu_stiu.get():
            self.mode = "stopwatch"
            self.time_seconds = 0
            self.target_seconds = 0
        else:
            self.mode = "countdown"
            self.target_seconds = int(self.spin_timp.get()) * 60
            self.time_seconds = self.target_seconds
        self.lbl_sess_materie.config(text=self.combo_disc.get())
        self.lbl_sess_notite.config(text=self.entry_notite.get() or "Fără notițe.")
        self.update_timer_display()
        self.frame_form.pack_forget()
        self.frame_timer.pack(fill="both", expand=True)
        self.running = True
        self.tick()

    def setup_timer(self):
        info = tk.Frame(self.frame_timer, bg=C_DARK_PURPLE, pady=20)
        info.pack(fill="x")
        self.lbl_sess_materie = tk.Label(info, text="", font=("Georgia", 18, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE)
        self.lbl_sess_materie.pack()
        self.lbl_sess_notite = tk.Label(info, text="", font=("Arial", 10, "italic"), bg=C_DARK_PURPLE,
                                        fg=C_LIGHT_PURPLE)
        self.lbl_sess_notite.pack()
        self.lbl_timer = tk.Label(self.frame_timer, text="00:00:00", font=("Arial", 60, "bold"), bg=C_LIGHT_PURPLE,
                                  fg=C_DARK_PURPLE)
        self.lbl_timer.pack(pady=40)
        self.btn_toggle = tk.Button(self.frame_timer, text="⏸ Pauză", font=("Arial", 14, "bold"), bg="#f5c8a8",
                                    width=15, command=self.toggle_timer)
        self.btn_toggle.pack()
        btns = tk.Frame(self.frame_timer, bg=C_LIGHT_PURPLE)
        btns.pack(pady=30)
        tk.Button(btns, text="❌ Anulează", bg="#f5a8c8", command=self.destroy).pack(side="left", padx=10)
        tk.Button(btns, text="⏳ Amână", bg="#a8c8f5", command=self.postpone).pack(side="left", padx=10)
        tk.Button(btns, text="✔ Finalizează", bg="#a8f5b8", command=self.finish).pack(side="left", padx=10)

    def tick(self):
        if self.running:
            if self.mode == "countdown" and self.time_seconds > 0:
                self.time_seconds -= 1
            else:
                self.time_seconds += 1
            self.elapsed_today += 1
            self.update_timer_display()
        self.after(1000, self.tick)

    def update_timer_display(self):
        m, s = divmod(self.time_seconds, 60)
        h, m = divmod(m, 60)
        self.lbl_timer.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def toggle_timer(self):
        self.running = not self.running
        self.btn_toggle.config(text="⏸ Pauză" if self.running else "▶ Continuă")

    def postpone(self):
        if self.resume_info:
            self.controller.planner_service.resume_study_session(self.resume_info['ses_id'],
                                                                 self.resume_info['data_str'],
                                                                 self.resume_info['total_secunde'], self.elapsed_today,
                                                                 "Nefinalizat")
        else:
            self.controller.planner_service.save_study_session(self.disciplina_aleasa, self.elapsed_today,
                                                               self.target_seconds, self.entry_notite.get(),
                                                               "Nefinalizat")
        self.on_close_callback()
        self.destroy()

    def finish(self):
        if self.resume_info:
            self.controller.planner_service.resume_study_session(self.resume_info['ses_id'],
                                                                 self.resume_info['data_str'],
                                                                 self.resume_info['total_secunde'], self.elapsed_today,
                                                                 "Finalizat")
        else:
            self.controller.planner_service.save_study_session(self.disciplina_aleasa, self.elapsed_today,
                                                               self.target_seconds, self.entry_notite.get(),
                                                               "Finalizat")
        self.on_close_callback()
        self.destroy()


class StudySessionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_LIGHT_PURPLE)
        self.controller = controller
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        tk.Label(self, text="Sesiuni de Studiu", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(pady=10)
        top = tk.Frame(self, bg=C_LIGHT_PURPLE)
        top.pack(fill="x", padx=40)
        self.calendar_frame = tk.Frame(top, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2, padx=10,
                                       pady=10)
        self.calendar_frame.pack(side="left", expand=True, fill="both")

        cal_nav = tk.Frame(self.calendar_frame, bg=C_WHITE)
        cal_nav.pack(fill="x")
        tk.Button(cal_nav, text="<", command=self.prev_month, relief="flat", bg=C_PANEL_BG).pack(side="left")
        self.lbl_month_year = tk.Label(cal_nav, text="", font=("Georgia", 14, "bold"), bg=C_WHITE, fg=C_DARK_PURPLE)
        self.lbl_month_year.pack(side="left", expand=True)
        tk.Button(cal_nav, text=">", command=self.next_month, relief="flat", bg=C_PANEL_BG).pack(side="right")
        self.cal_grid = tk.Frame(self.calendar_frame, bg=C_WHITE)
        self.cal_grid.pack(pady=5)

        btn_f = tk.Frame(top, bg=C_LIGHT_PURPLE, padx=20)
        btn_f.pack(side="right")
        self.canvas_btn = tk.Canvas(btn_f, width=130, height=130, bg=C_LIGHT_PURPLE, highlightthickness=0,
                                    cursor="hand2")
        self.canvas_btn.pack()
        self.canvas_btn.create_oval(5, 5, 125, 125, fill="#a8f5b8", outline=C_DARK_PURPLE, width=2)
        self.canvas_btn.create_text(65, 55, text="▶", font=("Arial", 24), fill=C_DARK_PURPLE)
        self.canvas_btn.create_text(65, 85, text="ÎNCEPE", font=("Georgia", 10, "bold"), fill=C_DARK_PURPLE)
        self.canvas_btn.bind("<Button-1>", self.open_timer)

        container = tk.Frame(self, bg=C_LIGHT_PURPLE)
        container.pack(fill="both", expand=True, padx=40, pady=10)
        self.canvas = tk.Canvas(container, bg=C_LIGHT_PURPLE, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=C_LIGHT_PURPLE)
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def prev_month(self):
        self.current_month = 12 if self.current_month == 1 else self.current_month - 1
        if self.current_month == 12: self.current_year -= 1
        self.render_calendar()

    def next_month(self):
        self.current_month = 1 if self.current_month == 12 else self.current_month + 1
        if self.current_month == 1: self.current_year += 1
        self.render_calendar()

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m" if h > 0 else f"{m}m {s}s"

    def refresh_data(self):
        if not self.controller.auth_service.current_user: return
        raw = self.controller.planner_service.get_study_sessions(self.controller.auth_service.current_user['id'])
        self.ses_data = sorted(raw, key=lambda x: x[1], reverse=True)
        self.render_calendar()

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        for label, status_val in [("⏳ AMÂNATE", "Nefinalizat"), ("✅ FINALIZATE", "Finalizat")]:
            tk.Label(self.scroll_frame, text=label, font=("Arial", 11, "bold"), bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE,
                     anchor="w").pack(fill="x", pady=(10, 0))
            filtered = [s for s in self.ses_data if s[4] == status_val]

            if not filtered:
                tk.Label(self.scroll_frame, text="Nimic aici.", font=("Arial", 9), bg=C_LIGHT_PURPLE,
                         fg="#777").pack(anchor="w", padx=20)
            for s in filtered:
                self.create_card(s)

    def render_calendar(self):
        for w in self.cal_grid.winfo_children(): w.destroy()
        luni = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie",
                "Octombrie", "Noiembrie", "Decembrie"]
        self.lbl_month_year.config(text=f"{luni[self.current_month - 1]} {self.current_year}")

        zile_studiate = set()
        for d in self.ses_data:
            data_str = str(d[1])

            # Tăiem eventualul "|Timp" (dacă e o sesiune veche amânată)
            if "|" in data_str:
                data_str = data_str.split('|')[0]

            # Despărțim în caz că are mai multe zile și curățăm spațiile (AICI ERA BUG-UL DE CALENDAR)
            dates = [zi.strip() for zi in data_str.split(',')]

            for dt_s in dates:
                try:
                    dt_obj = datetime.strptime(dt_s, "%d-%m-%Y")
                    if dt_obj.year == self.current_year and dt_obj.month == self.current_month:
                        zile_studiate.add(dt_obj.day)
                except:
                    pass

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, sapt in enumerate(cal):
            for c, zi in enumerate(sapt):
                if zi == 0: continue
                bg = "#a8f5b8" if zi in zile_studiate else C_WHITE
                lbl = tk.Label(self.cal_grid, text=str(zi), width=4, height=2, bg=bg, font=("Arial", 9, "bold"))
                lbl.grid(row=r, column=c, padx=1, pady=1)
                if zi in zile_studiate: lbl.config(fg=C_DARK_PURPLE)

    def create_card(self, s):
        ses_id, data_str, sec, note, status, mat, col, disc_id, tinta = s
        if not str(col).startswith('#'): col = DISC_COLORS_MAP.get(col, C_LIGHT_PURPLE)

        card = tk.Frame(self.scroll_frame, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2, padx=15,
                        pady=10)
        card.pack(fill="x", pady=5, padx=10)

        header = tk.Frame(card, bg=C_WHITE)
        header.pack(fill="x")
        canv = tk.Canvas(header, width=15, height=15, bg=C_WHITE, highlightthickness=0)
        canv.pack(side="left", padx=(0, 10))
        canv.create_oval(2, 2, 13, 13, fill=col, outline=col)
        tk.Label(header, text=mat, font=("Georgia", 13, "bold"), bg=C_WHITE, fg=C_DARK_PURPLE).pack(side="left")
        btn_t = tk.Button(header, text="▼", font=FONT_NORMAL, bg=C_WHITE, relief="flat", cursor="hand2")
        btn_t.pack(side="right")

        details = tk.Frame(card, bg=C_WHITE)
        display_t = self.format_time(sec)
        if tinta > 0: display_t += f" / {self.format_time(tinta)}"

        tk.Label(details, text=f"Timp: {display_t}", font=("Arial", 10, "bold"), bg=C_WHITE, fg="#555").pack(anchor="w",
                                                                                                             pady=2)
        tk.Label(details, text=f"Notițe: {note}", font=("Arial", 9), bg=C_WHITE, fg="#777").pack(anchor="w")

        b_f = tk.Frame(details, bg=C_WHITE)
        b_f.pack(fill="x", pady=5)

        # AICI ERA BUG-UL DE LA BUTOANELE DE ȘTERGE - Am forțat variabilele să se lege strict de ID-ul local (sid=ses_id)
        if status == "Nefinalizat":
            tk.Button(b_f, text="▶ Continuă", bg="#a8f5b8", font=("Arial", 9, "bold"), relief="flat",
                      command=lambda info={
                          'ses_id': ses_id, 'disc_id': disc_id, 'materie': mat, 'total_secunde': sec,
                          'durata_tinta': tinta, 'data_str': data_str, 'notite': note
                      }: self.open_timer(None, info)).pack(side="left", padx=5)

        tk.Button(b_f, text="Șterge", bg="#f5a8c8", font=("Arial", 9), relief="flat",
                  command=lambda sid=ses_id: self.delete_ses(sid)).pack(side="left")

        def toggle():
            if details.winfo_ismapped():
                details.pack_forget()
                btn_t.config(text="▼")
            else:
                details.pack(fill="x")
                btn_t.config(text="▲")

        btn_t.config(command=toggle)

    def open_timer(self, event=None, resume_info=None):
        raw_d = self.controller.planner_service.get_discipline(self.controller.auth_service.current_user['id'])
        if not raw_d and not resume_info:
            messagebox.showwarning("!", "Adaugă o materie întâi!")
            return
        d_map = {d[1]: d[0] for d in raw_d}
        TimerWindow(self, self.controller, d_map, self.refresh_data, resume_info)

    def delete_ses(self, sid):
        if messagebox.askyesno("Confirmare", "Sigur vrei să ștergi această sesiune?"):
            self.controller.planner_service.delete_session(sid)
            self.refresh_data()