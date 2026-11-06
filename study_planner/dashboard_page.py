import tkinter as tk
from tkinter import ttk, messagebox
from config import *

from discipline_page import DisciplinePage
from deadlines_page import DeadlinesPage
from study_sessions_page import StudySessionsPage
from progress_page import ProgressPage


class MainAppFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_DARK_PURPLE)
        self.controller = controller

        # ==========================================
        # TEMPLATE: SIDEBAR (Meniul din Stânga)
        # ==========================================
        self.sidebar = tk.Frame(self, bg=C_DARK_PURPLE, width=220)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="Study Planner", font=FONT_TITLE, bg=C_DARK_PURPLE, fg=C_WHITE).pack(pady=(20, 10))
        self.canvas_left = tk.Canvas(self.sidebar, height=2, bg=C_DARK_PURPLE, highlightthickness=0)
        self.canvas_left.create_line(10, 1, 220, 1, dash=(4, 4), fill=C_WHITE)
        self.canvas_left.pack(fill="x", pady=(0, 20))

        # Butoane Navigare
        self.create_nav_button("Home", lambda: self.show_content("Welcome"))
        self.create_nav_button("Discipline", lambda: self.show_content("Discipline"))
        self.create_nav_button("Deadlines", lambda: self.show_content("Deadlines"))
        self.create_nav_button("Study Sessions", lambda: self.show_content("Sessions"))

        # Zona Profil Utilizator
        self.user_profile_frame = tk.Frame(self.sidebar, bg=C_DARK_PURPLE, cursor="hand2")
        self.user_profile_frame.pack(side="bottom", fill="x", pady=20, padx=10)

        icon_canvas = tk.Canvas(self.user_profile_frame, width=40, height=40, bg=C_DARK_PURPLE, highlightthickness=0)
        icon_canvas.pack(side="left", padx=(10, 5))
        icon_canvas.create_oval(2, 2, 38, 38, outline=C_LIGHT_PURPLE, width=2)
        icon_canvas.create_oval(12, 8, 28, 24, outline=C_LIGHT_PURPLE, width=2)
        icon_canvas.create_arc(6, 20, 34, 48, start=0, extent=180, outline=C_LIGHT_PURPLE, width=2, style="arc")

        self.lbl_username_bottom = tk.Label(self.user_profile_frame, text="", font=("Georgia", 13, "italic"),
                                            bg=C_DARK_PURPLE, fg=C_LIGHT_PURPLE)
        self.lbl_username_bottom.pack(side="left")

        self.profile_menu = tk.Menu(self, tearoff=0, bg=C_WHITE, fg=C_DARK_PURPLE, font=FONT_NORMAL)
        self.profile_menu.add_command(label="Editează cont", command=lambda: self.show_content("EditAccount"))
        self.profile_menu.add_separator()
        self.profile_menu.add_command(label="Logout", command=self.do_logout)

        self.user_profile_frame.bind("<Button-1>", self.show_profile_menu)
        icon_canvas.bind("<Button-1>", self.show_profile_menu)
        self.lbl_username_bottom.bind("<Button-1>", self.show_profile_menu)

        # ==========================================
        # TEMPLATE: CONTENT AREA
        # ==========================================
        self.right_wrapper = tk.Frame(self, bg=C_DARK_PURPLE)
        self.right_wrapper.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        self.main_card = tk.Frame(self.right_wrapper, bg=C_LIGHT_PURPLE)
        self.main_card.pack(fill="both", expand=True)

        self.top_bar = tk.Frame(self.main_card, bg=C_LIGHT_PURPLE)
        self.top_bar.pack(fill="x")

        # CREARE BUTON PROGRES
        self.btn_progres = tk.Button(self.top_bar, text="Vezi Progres", font=("Arial", 10, "bold"),
                                     bg=C_WHITE, fg=C_DARK_PURPLE, relief="flat", cursor="hand2",
                                     command=lambda: self.show_content("Progress"))

        self.canvas_right = tk.Canvas(self.main_card, height=2, bg=C_LIGHT_PURPLE, highlightthickness=0)
        self.canvas_right.create_line(0, 1, 2000, 1, dash=(4, 4), fill=C_DARK_PURPLE)
        self.canvas_right.pack(fill="x", pady=(5, 0))

        self.views_container = tk.Frame(self.main_card, bg=C_LIGHT_PURPLE)
        self.views_container.pack(fill="both", expand=True)

        self.views = {}

        # Initializare View-uri
        self.view_welcome = tk.Frame(self.views_container, bg=C_LIGHT_PURPLE)
        self.lbl_hello = tk.Label(self.view_welcome, text="Hello", font=("Georgia", 36, "italic"), bg=C_LIGHT_PURPLE,
                                  fg=C_DARK_PURPLE)
        self.lbl_hello.place(relx=0.5, rely=0.5, anchor="center")
        self.views["Welcome"] = self.view_welcome

        self.view_disc = DisciplinePage(self.views_container, self.controller)
        self.views["Discipline"] = self.view_disc

        self.view_dead = DeadlinesPage(self.views_container, self.controller)
        self.views["Deadlines"] = self.view_dead

        self.view_ses = StudySessionsPage(self.views_container, self.controller)
        self.views["Sessions"] = self.view_ses

        self.view_edit_acc = tk.Frame(self.views_container, bg=C_LIGHT_PURPLE)
        self.setup_edit_account_temp()
        self.views["EditAccount"] = self.view_edit_acc

        # View Admin
        self.setup_admin_view()

        self.view_progress = ProgressPage(self.views_container, self.controller)
        self.views["Progress"] = self.view_progress

    def setup_admin_view(self):
        self.view_admin = tk.Frame(self.views_container, bg=C_LIGHT_PURPLE)
        tk.Label(self.view_admin, text="👑 Panou Control Administrator", font=FONT_TITLE, bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE).pack(pady=20)

        # --- ZONA 1: SETĂRI GLOBALE ---
        frame_setari = tk.Frame(self.view_admin, bg=C_PANEL_BG, padx=20, pady=15, highlightthickness=1,
                                highlightbackground=C_WHITE)
        frame_setari.pack(fill="x", padx=40, pady=(0, 20))

        tk.Label(frame_setari, text="⚙️ Setări Aplicație", font=("Georgia", 12, "bold"), bg=C_PANEL_BG,
                 fg=C_DARK_PURPLE).pack(anchor="w", pady=(0, 10))
        tk.Label(frame_setari, text="Sugestii de timp (minute, separate prin virgulă):", bg=C_PANEL_BG, fg="#555").pack(
            anchor="w")

        self.entry_sugestii = tk.Entry(frame_setari, font=FONT_NORMAL, bg=C_WHITE)
        self.entry_sugestii.pack(fill="x", pady=5, ipady=4)

        tk.Button(frame_setari, text="💾 Salvează Setările", bg=C_DARK_PURPLE, fg=C_WHITE, font=("Arial", 10, "bold"),
                  command=self.save_admin_settings, cursor="hand2").pack(anchor="w", pady=5, ipadx=10)

        # --- ZONA 2: LISTA UTILIZATORI ---
        tk.Label(self.view_admin, text="Lista utilizatorilor înregistrați:", font=FONT_NORMAL,
                 bg=C_LIGHT_PURPLE).pack(pady=5)
        self.listbox_users = tk.Listbox(self.view_admin, font=("Courier New", 11), width=70, height=12)
        self.listbox_users.pack(pady=10, padx=40, fill="both", expand=True)

        tk.Button(self.view_admin, text="🚪 Logout Admin", font=FONT_NORMAL, bg=C_WHITE, command=self.do_logout).pack(
            pady=20)
        self.views["Admin"] = self.view_admin

    def save_admin_settings(self):
        val = self.entry_sugestii.get()
        try:
            # Testăm dacă utilizatorul a introdus doar numere valide
            [int(x.strip()) for x in val.split(',')]
            self.controller.planner_service.update_sugestii_timp(val)
            messagebox.showinfo("Succes", "Setările au fost actualizate pentru toți studenții!")
        except ValueError:
            messagebox.showerror("Eroare", "Te rog introdu doar numere separate prin virgulă (ex: 15, 30, 45, 60)")

    def refresh_admin_list(self):
        # Încarcă sugestiile curente din DB în Entry
        sugestii = self.controller.planner_service.get_sugestii_timp()
        self.entry_sugestii.delete(0, tk.END)
        self.entry_sugestii.insert(0, ", ".join(map(str, sugestii)))

        self.listbox_users.delete(0, tk.END)
        users = self.controller.auth_service.repo.get_all_students()
        header = f"{'ID':<4} | {'Nume':<20} | {'Email':<25} | {'Rol':<10}"
        self.listbox_users.insert(tk.END, header)
        self.listbox_users.insert(tk.END, "-" * 70)
        for u in users:
            line = f"{u[0]:<4} | {u[1]:<20} | {u[2]:<25} | {u[3]:<10}"
            self.listbox_users.insert(tk.END, line)

    def load_dashboard(self):
        user = self.controller.auth_service.current_user
        if user:
            nume_utilizator = user.get('nume', 'Utilizator')
            self.lbl_hello.config(text=f"Hello, {nume_utilizator}!")
            self.lbl_username_bottom.config(text=nume_utilizator)

            # RESETARE TOTALĂ: Ascundem totul înainte de a decide rolul
            self.sidebar.pack_forget()
            self.btn_progres.pack_forget()

            if user.get('rol') == 'admin':
                # LOGICA ADMIN: Fără sidebar, fără buton progres
                self.right_wrapper.pack_configure(padx=20)
                self.show_content("Admin")
            else:
                # LOGICA STUDENT: Punem sidebar-ul și butonul o singură dată
                self.sidebar.pack(side="left", fill="y")
                self.btn_progres.pack(side="left", padx=40, pady=(15, 5), ipadx=10, ipady=2)
                self.right_wrapper.pack_configure(padx=(0, 20))
                self.show_content("Welcome")

    def show_content(self, view_name):
        if view_name == "Admin":
            self.refresh_admin_list()
        elif view_name == "Progress":
            self.view_progress.refresh_statistics()
        for v in self.views.values():
            v.pack_forget()
        self.views[view_name].pack(fill="both", expand=True)

        if view_name == "Discipline":
            self.view_disc.show_view("List")
        elif view_name == "Deadlines":
            self.view_dead.show_view("List")
        elif view_name == "Sessions":
            self.view_ses.refresh_data()
        elif view_name == "EditAccount":
            self.prefill_account_data()

    def show_profile_menu(self, event):
        self.profile_menu.tk_popup(event.x_root, event.y_root - 70)

    def do_logout(self):
        self.controller.auth_service.current_user = None
        self.controller.show_frame("LoginFrame")

    def create_nav_button(self, text, cmd):
        btn = tk.Button(self.sidebar, text=text, font=FONT_MENU, bg=C_DARK_PURPLE, fg=C_WHITE,
                        activebackground=C_LIGHT_PURPLE, activeforeground=C_DARK_PURPLE, relief="flat", cursor="hand2",
                        command=cmd)
        btn.pack(fill="x", padx=10, pady=10)

    def setup_edit_account_temp(self):
        tk.Label(self.view_edit_acc, text="Editează Profilul", font=FONT_TITLE, bg=C_LIGHT_PURPLE,
                 fg=C_DARK_PURPLE).pack(pady=(30, 20))
        form_frame = tk.Frame(self.view_edit_acc, bg=C_PANEL_BG, padx=40, pady=40, highlightbackground=C_WHITE,
                              highlightthickness=1)
        form_frame.pack(fill="x", padx=80)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Numele tău:", bg=C_PANEL_BG, font=FONT_NORMAL).grid(row=0, column=0, sticky="w",
                                                                                       pady=10)
        self.entry_acc_nume = tk.Entry(form_frame, font=FONT_NORMAL, bg=C_WHITE)
        self.entry_acc_nume.grid(row=0, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Email:", bg=C_PANEL_BG, font=FONT_NORMAL).grid(row=1, column=0, sticky="w", pady=10)
        self.entry_acc_email = tk.Entry(form_frame, font=FONT_NORMAL, bg=C_WHITE)
        self.entry_acc_email.grid(row=1, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Label(form_frame, text="Parolă nouă:", bg=C_PANEL_BG, font=FONT_NORMAL).grid(row=2, column=0, sticky="w",
                                                                                        pady=10)
        self.entry_acc_parola = tk.Entry(form_frame, font=FONT_NORMAL, bg=C_WHITE)
        self.entry_acc_parola.grid(row=2, column=1, sticky="ew", padx=15, pady=10, ipady=5)

        tk.Button(form_frame, text="Salvează Modificările", font=("Georgia", 12, "bold"), bg=C_DARK_PURPLE, fg=C_WHITE,
                  command=self.update_account_info).grid(row=3, column=0, columnspan=2, pady=(30, 0), ipady=8, ipadx=20)

    def prefill_account_data(self):
        user = self.controller.auth_service.current_user
        if user:
            self.entry_acc_nume.delete(0, tk.END)
            self.entry_acc_nume.insert(0, user.get('nume', ''))
            self.entry_acc_email.delete(0, tk.END)
            self.entry_acc_email.insert(0, user.get('email', ''))
            self.entry_acc_parola.delete(0, tk.END)
            self.entry_acc_parola.insert(0, user.get('parola', ''))

    def update_account_info(self):
        nume, email, parola = self.entry_acc_nume.get(), self.entry_acc_email.get(), self.entry_acc_parola.get()
        if self.controller.auth_service.update_account(nume, email, parola):
            messagebox.showinfo("Succes", "Date actualizate!")
            self.lbl_hello.config(text=f"Hello, {nume}!")
            self.lbl_username_bottom.config(text=nume)
        else:
            messagebox.showerror("Eroare", "Email deja existent!")