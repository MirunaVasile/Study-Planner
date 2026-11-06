# discipline_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from config import *


class DisciplinePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_LIGHT_PURPLE)
        self.controller = controller
        self.editing_disc_id = None

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

        if view_name == "List":
            self.refresh_list()

    # ==========================================
    # 1. VIEW: LISTA CU CARDURI EXPANDABILE
    # ==========================================
    def setup_list_view(self):
        tk.Label(self.view_list, text="Gestionare Discipline", font=FONT_TITLE, bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE).pack(pady=(20, 10))

        container = tk.Frame(self.view_list, bg=C_LIGHT_PURPLE)
        container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.canvas = tk.Canvas(container, bg=C_LIGHT_PURPLE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=C_LIGHT_PURPLE)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Salvăm ID-ul ferestrei din canvas pentru a-i putea modifica lățimea dinamic
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Funcție care forțează cardurile să se întindă pe toată lățimea disponibilă!
        def configure_canvas_width(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", configure_canvas_width)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_add_fab = tk.Button(self.view_list, text="➕ Adaugă Materie", font=("Arial", 12, "bold"), bg=C_DARK_PURPLE,
                                fg=C_WHITE, relief="flat", cursor="hand2", command=lambda: self.show_view("Add"))
        btn_add_fab.place(relx=0.95, rely=0.95, anchor="se")

    def refresh_list(self):
        user = self.controller.auth_service.current_user
        if not user: return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.disciplina_data = self.controller.planner_service.get_discipline(user['id'])

        if not self.disciplina_data:
            tk.Label(self.scrollable_frame, text="Nu ai adăugat nicio materie încă.", font=FONT_NORMAL,
                     bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(pady=20)
            return

        for d in self.disciplina_data:
            self.create_card(d)

    def create_card(self, disc_data):
        disc_id, denumire, profesor, credite, hex_color = disc_data

        # --- FIX PENTRU DATELE VECHI DIN BAZA DE DATE ---
        # Dacă culoarea salvată este goală sau este un text vechi (ex "Albastru") în loc de "#...", o corectăm.
        if not hex_color or not str(hex_color).startswith('#'):
            hex_color = DISC_COLORS_MAP.get(hex_color,
                                            C_LIGHT_PURPLE)  # Preia HEX-ul dacă găsește numele, altfel mov deschis.

        card = tk.Frame(self.scrollable_frame, bg=C_WHITE, highlightbackground=C_PANEL_BG, highlightthickness=2,
                        padx=15, pady=10)
        card.pack(fill="x", pady=10, padx=10)  # Acum se va întinde pe tot ecranul

        header = tk.Frame(card, bg=C_WHITE)
        header.pack(fill="x")

        canvas_color = tk.Canvas(header, width=20, height=20, bg=C_WHITE, highlightthickness=0)
        canvas_color.pack(side="left", padx=(0, 15))
        canvas_color.create_oval(2, 2, 18, 18, fill=hex_color, outline=hex_color)

        tk.Label(header, text=denumire, font=("Georgia", 14, "bold"), bg=C_WHITE, fg=C_DARK_PURPLE).pack(side="left")

        btn_toggle = tk.Button(header, text="▼", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE, relief="flat",
                               cursor="hand2")
        btn_toggle.pack(side="right")

        details = tk.Frame(card, bg=C_WHITE)

        tk.Label(details, text=f"Profesor: {profesor}", font=FONT_NORMAL, bg=C_WHITE, fg="#555").grid(row=0, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=(10, 5))
        tk.Label(details, text=f"Credite: {credite}", font=FONT_NORMAL, bg=C_WHITE, fg="#555").grid(row=1, column=0,
                                                                                                    sticky="w",
                                                                                                    pady=(0, 10))

        btn_frame = tk.Frame(details, bg=C_WHITE)
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=(40, 0))
        details.columnconfigure(1, weight=1)

        btn_edit = tk.Button(btn_frame, text="Editează", bg="#a8c8f5", fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                             command=lambda: self.open_edit(disc_data))
        btn_edit.pack(side="left", padx=5, ipady=3, ipadx=5)

        btn_delete = tk.Button(btn_frame, text="Șterge", bg="#f5a8c8", fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                               command=lambda: self.delete_disc(disc_id))
        btn_delete.pack(side="left", padx=5, ipady=3, ipadx=5)

        def toggle_details(evt=None):
            if details.winfo_ismapped():
                details.pack_forget()
                btn_toggle.config(text="▼")
            else:
                details.pack(fill="x", expand=True)
                btn_toggle.config(text="▲")

        btn_toggle.config(command=toggle_details)

    # ==========================================
    # 2. VIEW: FORMULAR ADAUGARE
    # ==========================================
    def setup_add_view(self):
        tk.Label(self.view_add, text="Adaugă o materie nouă", font=FONT_TITLE, bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE).pack(pady=(30, 20))
        form_frame = tk.Frame(self.view_add, bg=C_PANEL_BG, padx=40, pady=40, highlightbackground=C_WHITE,
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=80)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Nume Materie:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=0,
                                                                                                           column=0,
                                                                                                           sticky="w",
                                                                                                           pady=10)
        self.entry_add_nume = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_add_nume.grid(row=0, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Profesor:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=1, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=10)
        self.entry_add_prof = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_add_prof.grid(row=1, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Credite:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=2, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=10)
        self.entry_add_cred = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_add_cred.grid(row=2, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Culoare Etichetă:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=3,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               pady=10)
        self.combo_add_culoare = ttk.Combobox(form_frame, values=DISC_COLORS_LIST, state="readonly", font=FONT_NORMAL)
        self.combo_add_culoare.set(DISC_COLORS_LIST[0])
        self.combo_add_culoare.grid(row=3, column=1, sticky="w", padx=15, pady=10)

        btn_save = tk.Button(form_frame, text="Salvează", font=("Georgia", 12, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE,
                             relief="flat", cursor="hand2", command=self.submit_add)
        btn_save.grid(row=4, column=0, columnspan=2, pady=(20, 0), ipady=8, ipadx=20)

        btn_cancel = tk.Button(form_frame, text="Anulează", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE,
                               relief="flat", cursor="hand2", command=lambda: self.show_view("List"))
        btn_cancel.grid(row=5, column=0, columnspan=2, pady=(10, 0))

    def submit_add(self):
        try:
            nume = self.entry_add_nume.get()
            prof = self.entry_add_prof.get()
            credite = self.entry_add_cred.get()
            cod_hex = DISC_COLORS_MAP.get(self.combo_add_culoare.get(), C_LIGHT_PURPLE)

            if not nume.strip(): raise ValueError("Numele materiei este obligatoriu!")

            self.controller.planner_service.add_disciplina(self.controller.auth_service.current_user['id'], nume, prof,
                                                           credite, cod_hex)

            self.entry_add_nume.delete(0, tk.END)
            self.entry_add_prof.delete(0, tk.END)
            self.entry_add_cred.delete(0, tk.END)
            self.combo_add_culoare.set(DISC_COLORS_LIST[0])

            messagebox.showinfo("Succes", "Disciplina a fost adăugată!")
            self.show_view("List")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    # ==========================================
    # 3. VIEW: FORMULAR EDITARE
    # ==========================================
    def setup_edit_view(self):
        tk.Label(self.view_edit, text="Editează materia", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(
            pady=(30, 20))
        form_frame = tk.Frame(self.view_edit, bg=C_PANEL_BG, padx=40, pady=40, highlightbackground=C_WHITE,
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=80)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Nume Materie:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=0,
                                                                                                           column=0,
                                                                                                           sticky="w",
                                                                                                           pady=10)
        self.entry_edit_nume = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_edit_nume.grid(row=0, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Profesor:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=1, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=10)
        self.entry_edit_prof = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_edit_prof.grid(row=1, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Credite:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=2, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=10)
        self.entry_edit_cred = tk.Entry(form_frame, font=FONT_NORMAL, relief="flat", bg=C_WHITE)
        self.entry_edit_cred.grid(row=2, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Culoare Etichetă:", bg=C_PANEL_BG, fg=C_DARK_PURPLE, font=FONT_NORMAL).grid(row=3,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               pady=10)
        self.combo_edit_culoare = ttk.Combobox(form_frame, values=DISC_COLORS_LIST, state="readonly", font=FONT_NORMAL)
        self.combo_edit_culoare.grid(row=3, column=1, sticky="w", padx=15, pady=10)

        btn_save = tk.Button(form_frame, text="Salvează Modificările", font=("Georgia", 12, "bold"), bg=C_DARK_PURPLE,
                             fg=C_WHITE, relief="flat", cursor="hand2", command=self.submit_edit)
        btn_save.grid(row=4, column=0, columnspan=2, pady=(20, 0), ipady=8, ipadx=20)

        btn_cancel = tk.Button(form_frame, text="Anulează", font=FONT_NORMAL, bg=C_WHITE, fg=C_DARK_PURPLE,
                               relief="flat", cursor="hand2", command=lambda: self.show_view("List"))
        btn_cancel.grid(row=5, column=0, columnspan=2, pady=(10, 0))

    def open_edit(self, disc_data):
        disc_id, denumire, profesor, credite, hex_color = disc_data
        self.editing_disc_id = disc_id

        self.entry_edit_nume.delete(0, tk.END)
        self.entry_edit_nume.insert(0, denumire)

        self.entry_edit_prof.delete(0, tk.END)
        self.entry_edit_prof.insert(0, profesor)

        self.entry_edit_cred.delete(0, tk.END)
        self.entry_edit_cred.insert(0, str(credite))

        nume_culoare = [k for k, v in DISC_COLORS_MAP.items() if v == hex_color]
        self.combo_edit_culoare.set(nume_culoare[0] if nume_culoare else DISC_COLORS_LIST[0])

        self.show_view("Edit")

    def submit_edit(self):
        try:
            nume = self.entry_edit_nume.get()
            prof = self.entry_edit_prof.get()
            credite = self.entry_edit_cred.get()
            cod_hex = DISC_COLORS_MAP.get(self.combo_edit_culoare.get(), C_LIGHT_PURPLE)

            self.controller.planner_service.update_disciplina(self.editing_disc_id, nume, prof, credite, cod_hex)
            messagebox.showinfo("Succes", "Materia a fost actualizată!")
            self.show_view("List")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def delete_disc(self, disc_id):
        raspuns = messagebox.askyesno("Confirmare",
                                      "Sigur vrei să ștergi materia? Se vor pierde și deadline-urile asociate.")
        if raspuns:
            self.controller.planner_service.delete_disciplina(disc_id)
            self.refresh_list()