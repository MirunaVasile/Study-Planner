# deadlines_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
from config import *


class DeadlinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_LIGHT_PURPLE)
        self.controller = controller
        self.editing_dead_id = None
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.frames = {}

        self.view_list = tk.Frame(self, bg=C_LIGHT_PURPLE)
        self.setup_list_view()
        self.frames["List"] = self.view_list

        self.view_add = tk.Frame(self, bg=C_LIGHT_PURPLE)
        self.setup_add_view()
        self.frames["Add"] = self.view_add

        self.view_edit = tk.Frame(self, bg=C_LIGHT_PURPLE)
        self.setup_edit_view()
        self.frames["Edit"] = self.view_edit

        self.show_view("List")

    def show_view(self, view_name):
        for frame in self.frames.values():
            frame.pack_forget()

        self.frames[view_name].pack(fill="both", expand=True)

        # AICI E REPARAȚIA:
        if view_name == "List":
            self.refresh_data()
        elif view_name == "Add":
            # Când deschidem formularul de adăugare, încărcăm instant materiile!
            self.refresh_disciplines_dropdown(self.combo_add_disc)


    # 1. VIEW: CALENDAR + LISTA CARDURI
    # ==========================================
    def setup_list_view(self):
        tk.Label(self.view_list, text="Deadlines & Calendar", font=FONT_TITLE, bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE).pack(pady=(20, 10))

        # --- ZONA CALENDAR ---
        self.calendar_frame = tk.Frame(self.view_list, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2,
                                       padx=10, pady=10)
        self.calendar_frame.pack(fill="x", padx=40, pady=(0, 20))

        self.cal_header = tk.Frame(self.calendar_frame, bg=C_WHITE)
        self.cal_header.pack(fill="x")
        tk.Button(self.cal_header, text="<", font=("Arial", 12, "bold"), bg=C_PANEL_BG, fg=C_DARK_PURPLE, relief="flat",
                  command=self.prev_month).pack(side="left", padx=10)
        self.lbl_month_year = tk.Label(self.cal_header, text="", font=("Georgia", 14, "bold"), bg=C_WHITE,
                                       fg=C_DARK_PURPLE)
        self.lbl_month_year.pack(side="left", expand=True)
        tk.Button(self.cal_header, text=">", font=("Arial", 12, "bold"), bg=C_PANEL_BG, fg=C_DARK_PURPLE, relief="flat",
                  command=self.next_month).pack(side="right", padx=10)

        self.cal_grid = tk.Frame(self.calendar_frame, bg=C_WHITE)
        self.cal_grid.pack(pady=10)

        # --- ZONA LISTĂ SCROLLABILĂ ---
        container = tk.Frame(self.view_list, bg=C_LIGHT_PURPLE)
        container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.canvas = tk.Canvas(container, bg=C_LIGHT_PURPLE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=C_LIGHT_PURPLE)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buton FAB
        btn_add_fab = tk.Button(self.view_list, text="➕ Adaugă Deadline", font=("Arial", 12, "bold"), bg=C_DARK_PURPLE,
                                fg=C_WHITE, relief="flat", cursor="hand2", command=lambda: self.show_view("Add"))
        btn_add_fab.place(relx=0.95, rely=0.95, anchor="se")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12; self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1; self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar()

    def refresh_data(self):
        user = self.controller.auth_service.current_user
        if not user: return

        raw_data = self.controller.planner_service.get_deadlines(user['id'])

        def parse_date(d_str):
            try:
                return datetime.strptime(d_str, "%d-%m-%Y")
            except ValueError:
                return datetime.max

        urmeaza = []
        finalizate = []

        for d in raw_data:
            status = d[7]
            if status == "Finalizat":
                finalizate.append(d)
            else:
                urmeaza.append(d)

        self.urmeaza_data = sorted(urmeaza, key=lambda x: parse_date(x[2]))
        self.finalizate_data = sorted(finalizate, key=lambda x: parse_date(x[2]))

        self.render_calendar()

        for widget in self.scrollable_frame.winfo_children(): widget.destroy()

        # Afișăm secțiunea "URMEAZĂ"
        tk.Label(self.scrollable_frame, text="⏳ URMEAZĂ", font=("Arial", 12, "bold"), bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE, anchor="w").pack(fill="x", padx=10, pady=(10, 0))
        if not self.urmeaza_data:
            tk.Label(self.scrollable_frame, text="Niciun deadline pe listă!", font=FONT_NORMAL, bg=C_LIGHT_PURPLE,
                     fg="#555").pack(pady=10)
        else:
            for d in self.urmeaza_data: self.create_card(d)

        # Afișăm secțiunea "FINALIZATE"
        tk.Label(self.scrollable_frame, text="✅ FINALIZATE", font=("Arial", 12, "bold"), bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE, anchor="w").pack(fill="x", padx=10, pady=(20, 0))
        if not self.finalizate_data:
            tk.Label(self.scrollable_frame, text="Încă nu ai finalizat nicio temă.", font=FONT_NORMAL,
                     bg=C_LIGHT_PURPLE, fg="#555").pack(pady=10)
        else:
            for d in self.finalizate_data: self.create_card(d)

    def render_calendar(self):
        for widget in self.cal_grid.winfo_children(): widget.destroy()

        luni = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie",
                "Octombrie", "Noiembrie", "Decembrie"]
        self.lbl_month_year.config(text=f"{luni[self.current_month - 1]} {self.current_year}")

        zile_sapt = ["L", "M", "M", "J", "V", "S", "D"]
        for col, zi in enumerate(zile_sapt):
            tk.Label(self.cal_grid, text=zi, font=("Arial", 10, "bold"), bg=C_WHITE, fg="#888", width=4).grid(row=0,
                                                                                                              column=col,
                                                                                                              pady=5)

        # Analizăm zilele pentru a ști ce desenăm pe calendar
        zile_info = {}
        for d in (self.urmeaza_data + self.finalizate_data):
            try:
                dt = datetime.strptime(d[2], "%d-%m-%Y")
                if dt.year == self.current_year and dt.month == self.current_month:
                    zi = dt.day
                    status = d[7]
                    culoare = d[5] if str(d[5]).startswith('#') else DISC_COLORS_MAP.get(d[5], C_DARK_PURPLE)

                    is_overdue = dt.date() < datetime.now().date() and status != "Finalizat"

                    if zi not in zile_info:
                        zile_info[zi] = {'bg': culoare, 'overdue': False, 'completed': False}

                    if is_overdue: zile_info[zi]['overdue'] = True
                    if status == "Finalizat": zile_info[zi]['completed'] = True
            except:
                pass

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for rand, saptamana in enumerate(cal):
            for col, zi in enumerate(saptamana):
                if zi == 0: continue

                # Canvas pentru fiecare zi, astfel încât să putem desena cerc/bifă
                c = tk.Canvas(self.cal_grid, width=32, height=32, bg=C_WHITE, highlightthickness=0)
                c.grid(row=rand + 1, column=col, padx=2, pady=2)

                fg_color = C_DARK_PURPLE

                if zi in zile_info:
                    # Desenam fundalul cu culoarea materiei
                    c.configure(bg=zile_info[zi]['bg'])
                    fg_color = C_WHITE

                    # Dacă este depășit -> Cerc ROȘU
                    if zile_info[zi]['overdue']:
                        c.create_oval(2, 2, 30, 30, outline="red", width=3)

                    # Dacă este finalizat -> Bifă
                    if zile_info[zi]['completed']:
                        c.create_text(24, 24, text="✔", fill="white", font=("Arial", 12, "bold"))

                elif zi == datetime.now().day and self.current_month == datetime.now().month and self.current_year == datetime.now().year:
                    c.configure(bg=C_PANEL_BG)

                c.create_text(16, 16, text=str(zi), font=("Arial", 10, "bold"), fill=fg_color)

    def create_card(self, dead_data):
        dead_id, titlu, data_limita, descriere, nume_materie, hex_color, disc_id, status = dead_data
        if not str(hex_color).startswith('#'): hex_color = DISC_COLORS_MAP.get(hex_color, C_LIGHT_PURPLE)

        # Verificare Overdue (Depășit)
        is_overdue = False
        try:
            dt = datetime.strptime(data_limita, "%d-%m-%Y")
            if dt.date() < datetime.now().date() and status != "Finalizat":
                is_overdue = True
        except:
            pass

        card = tk.Frame(self.scrollable_frame, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2,
                        padx=15, pady=10)
        card.pack(fill="x", pady=5, padx=10)

        header = tk.Frame(card, bg=C_WHITE)
        header.pack(fill="x")

        canvas_color = tk.Canvas(header, width=20, height=20, bg=C_WHITE, highlightthickness=0)
        canvas_color.pack(side="left", padx=(0, 15))
        canvas_color.create_oval(2, 2, 18, 18, fill=hex_color, outline=hex_color)

        # Font diferit (Tăiat) dacă e finalizat
        font_titlu = ("Georgia", 14, "overstrike") if status == "Finalizat" else ("Georgia", 14, "bold")
        tk.Label(header, text=titlu, font=font_titlu, bg=C_WHITE, fg=C_DARK_PURPLE).pack(side="left")

        # Săgeata Dropdown și Semnul de exclamare (Dacă e cazul)
        btn_toggle = tk.Button(header, text="▼", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE, relief="flat",
                               cursor="hand2")
        btn_toggle.pack(side="right")

        if is_overdue:
            tk.Label(header, text="❗", font=("Arial", 14, "bold"), bg=C_WHITE, fg="red").pack(side="right", padx=10)

        details = tk.Frame(card, bg=C_WHITE)
        tk.Label(details, text=f"Dată limită: {data_limita}", font=FONT_NORMAL, bg=C_WHITE,
                 fg="#d9534f" if is_overdue else "#555").grid(row=0, column=0, sticky="w", pady=(10, 5))
        tk.Label(details, text=f"Materie: {nume_materie}", font=FONT_NORMAL, bg=C_WHITE, fg="#555").grid(row=1,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         pady=(0, 5))
        tk.Label(details, text=f"Indicații: {descriere}", font=FONT_NORMAL, bg=C_WHITE, fg="#555").grid(row=2, column=0,
                                                                                                        sticky="w",
                                                                                                        pady=(0, 10))

        btn_frame = tk.Frame(details, bg=C_WHITE)
        btn_frame.grid(row=0, column=1, rowspan=3, sticky="e", padx=(40, 0))
        details.columnconfigure(1, weight=1)

        # Buton Finalizeaza (Vizibil doar daca nu e inca finalizat)
        if status != "Finalizat":
            tk.Button(btn_frame, text="✔ Finalizează", bg="#a8f5b8", fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                      font=("Arial", 10, "bold"), command=lambda: self.mark_completed(dead_id)).pack(side="left",
                                                                                                     padx=5, ipady=3,
                                                                                                     ipadx=5)

        tk.Button(btn_frame, text="Editează", bg="#a8c8f5", fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                  command=lambda: self.open_edit(dead_data)).pack(side="left", padx=5, ipady=3, ipadx=5)
        tk.Button(btn_frame, text="Șterge", bg="#f5a8c8", fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                  command=lambda: self.delete_deadline(dead_id)).pack(side="left", padx=5, ipady=3, ipadx=5)

        def toggle_details(evt=None):
            if details.winfo_ismapped():
                details.pack_forget()
                btn_toggle.config(text="▼")
            else:
                details.pack(fill="x", expand=True)
                btn_toggle.config(text="▲")

        btn_toggle.config(command=toggle_details)

    def mark_completed(self, dead_id):
        if messagebox.askyesno("Confirmare Finalizare", "Ești sigur că s-a finalizat această temă?"):
            self.controller.planner_service.mark_deadline_completed(dead_id)
            self.refresh_data()

    # ==========================================
    # PĂRȚILE COMUNE: COMBOBOX DATE, ADD/EDIT
    # ==========================================
    def create_date_picker(self, parent):
        # Aici am rescris folosind un GRID pentru a pune textele (Ziua, Luna, Anul) exact sub combobox-uri
        frame = tk.Frame(parent, bg=C_PANEL_BG)
        zile = [f"{i:02d}" for i in range(1, 32)]
        luni = [f"{i:02d}" for i in range(1, 13)]
        ani = [str(i) for i in range(2024, 2030)]

        combo_z = ttk.Combobox(frame, values=zile, width=4, state="readonly", font=FONT_NORMAL)
        combo_z.set(zile[0]);
        combo_z.grid(row=0, column=0, padx=2)
        tk.Label(frame, text="ziua", bg=C_PANEL_BG, fg="#888", font=("Arial", 8)).grid(row=1, column=0)

        tk.Label(frame, text="-", bg=C_PANEL_BG).grid(row=0, column=1)

        combo_l = ttk.Combobox(frame, values=luni, width=4, state="readonly", font=FONT_NORMAL)
        combo_l.set(luni[0]);
        combo_l.grid(row=0, column=2, padx=2)
        tk.Label(frame, text="luna", bg=C_PANEL_BG, fg="#888", font=("Arial", 8)).grid(row=1, column=2)

        tk.Label(frame, text="-", bg=C_PANEL_BG).grid(row=0, column=3)

        combo_a = ttk.Combobox(frame, values=ani, width=6, state="readonly", font=FONT_NORMAL)
        combo_a.set(str(datetime.now().year));
        combo_a.grid(row=0, column=4, padx=2)
        tk.Label(frame, text="anul", bg=C_PANEL_BG, fg="#888", font=("Arial", 8)).grid(row=1, column=4)

        return frame, combo_z, combo_l, combo_a

    def refresh_disciplines_dropdown(self, combo_widget):
        user = self.controller.auth_service.current_user
        data = self.controller.planner_service.get_discipline(user['id'])
        self.disc_map = {d[1]: d[0] for d in data}
        combo_widget['values'] = list(self.disc_map.keys())
        if self.disc_map: combo_widget.set(list(self.disc_map.keys())[0])

    # --- FORMULAR ADAUGARE ---
    def setup_add_view(self):
        tk.Label(self.view_add, text="Adaugă Deadline Nou", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(
            pady=(30, 20))
        form_frame = tk.Frame(self.view_add, bg=C_PANEL_BG, padx=40, pady=40, highlightbackground=C_WHITE,
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=80)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Titlu Sarcină:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=10)
        self.entry_add_titlu = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_add_titlu.grid(row=0, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Materia:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=1, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=10)
        self.combo_add_disc = ttk.Combobox(form_frame, state="readonly", font=FONT_NORMAL)
        self.combo_add_disc.grid(row=1, column=1, sticky="w", padx=15, pady=10)

        tk.Label(form_frame, text="Indicații (Info):", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=2,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               pady=10)
        self.entry_add_info = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_add_info.grid(row=2, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Data Limită:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=3,
                                                                                                          column=0,
                                                                                                          sticky="w",
                                                                                                          pady=10)
        self.frame_add_date, self.add_z, self.add_l, self.add_a = self.create_date_picker(form_frame)
        self.frame_add_date.grid(row=3, column=1, sticky="w", padx=15, pady=10)

        tk.Button(form_frame, text="Salvează Deadline", font=("Georgia", 12, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE,
                  relief="flat", cursor="hand2", command=self.submit_add).grid(row=4, column=0, columnspan=2,
                                                                               pady=(20, 0), ipady=8, ipadx=20)
        tk.Button(form_frame, text="Anulează", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE, relief="flat",
                  cursor="hand2", command=lambda: self.show_view("List")).grid(row=5, column=0, columnspan=2,
                                                                               pady=(10, 0))

    def submit_add(self):
        try:
            titlu = self.entry_add_titlu.get()
            info = self.entry_add_info.get()
            nume_disc = self.combo_add_disc.get()
            data_str = f"{self.add_z.get()}-{self.add_l.get()}-{self.add_a.get()}"

            if not titlu.strip() or not nume_disc: raise ValueError("Completează titlul și alege o materie!")

            disc_id = self.disc_map[nume_disc]
            self.controller.planner_service.add_deadline(disc_id, titlu, info, data_str)

            self.entry_add_titlu.delete(0, tk.END)
            self.entry_add_info.delete(0, tk.END)
            messagebox.showinfo("Succes", "Deadline adăugat!")
            self.show_view("List")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    # --- FORMULAR EDITARE ---
    def setup_edit_view(self):
        tk.Label(self.view_edit, text="Editează Deadline", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(
            pady=(30, 20))
        form_frame = tk.Frame(self.view_edit, bg=C_PANEL_BG, padx=40, pady=40, highlightbackground=C_WHITE,
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=80)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Titlu Sarcină:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=10)
        self.entry_edit_titlu = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_edit_titlu.grid(row=0, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Materia:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=1, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=10)
        self.combo_edit_disc = ttk.Combobox(form_frame, state="readonly", font=FONT_NORMAL)
        self.combo_edit_disc.grid(row=1, column=1, sticky="w", padx=15, pady=10)

        tk.Label(form_frame, text="Indicații (Info):", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=2,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               pady=10)
        self.entry_edit_info = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_edit_info.grid(row=2, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Data Limită:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=3,
                                                                                                          column=0,
                                                                                                          sticky="w",
                                                                                                          pady=10)
        self.frame_edit_date, self.edit_z, self.edit_l, self.edit_a = self.create_date_picker(form_frame)
        self.frame_edit_date.grid(row=3, column=1, sticky="w", padx=15, pady=10)

        tk.Button(form_frame, text="Salvează Modificările", font=("Georgia", 12, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE,
                  relief="flat", cursor="hand2", command=self.submit_edit).grid(row=4, column=0, columnspan=2,
                                                                                pady=(20, 0), ipady=8, ipadx=20)
        tk.Button(form_frame, text="Anulează", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE, relief="flat",
                  cursor="hand2", command=lambda: self.show_view("List")).grid(row=5, column=0, columnspan=2,
                                                                               pady=(10, 0))

    def open_edit(self, dead_data):
        self.refresh_disciplines_dropdown(self.combo_edit_disc)

        dead_id, titlu, data_limita, descriere, nume_materie, hex_color, disc_id, status = dead_data
        self.editing_dead_id = dead_id

        self.entry_edit_titlu.delete(0, tk.END)
        self.entry_edit_titlu.insert(0, titlu)

        self.combo_edit_disc.set(nume_materie)

        self.entry_edit_info.delete(0, tk.END)
        self.entry_edit_info.insert(0, descriere)

        try:
            z, l, a = data_limita.split('-')
            self.edit_z.set(z);
            self.edit_l.set(l);
            self.edit_a.set(a)
        except:
            pass

        self.show_view("Edit")

    def submit_edit(self):
        try:
            titlu = self.entry_edit_titlu.get()
            info = self.entry_edit_info.get()
            nume_disc = self.combo_edit_disc.get()
            data_str = f"{self.edit_z.get()}-{self.edit_l.get()}-{self.edit_a.get()}"

            if not titlu.strip(): raise ValueError("Titlul este obligatoriu!")

            disc_id = self.disc_map[nume_disc]
            self.controller.planner_service.update_deadline(self.editing_dead_id, disc_id, titlu, info, data_str)

            messagebox.showinfo("Succes", "Deadline actualizat!")
            self.show_view("List")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def delete_deadline(self, dead_id):
        if messagebox.askyesno("Confirmare", "Sigur vrei să ștergi acest deadline?"):
            self.controller.planner_service.delete_deadline(dead_id)
            self.refresh_data()