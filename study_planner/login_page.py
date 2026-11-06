# login_page.py
import tkinter as tk
from tkinter import messagebox
from config import *


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_DARK_PURPLE)
        self.controller = controller

        panel = tk.Frame(self, bg=C_LIGHT_PURPLE, padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(panel, text="Study Planner", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(pady=(0, 20))

        tk.Label(panel, text="Email", font=FONT_NORMAL, bg=C_LIGHT_PURPLE).pack(anchor="w")
        self.email_entry = tk.Entry(panel, font=FONT_NORMAL, width=30, relief="flat")
        self.email_entry.pack(pady=(0, 15), ipady=5)

        tk.Label(panel, text="Parolă", font=FONT_NORMAL, bg=C_LIGHT_PURPLE).pack(anchor="w")
        self.pass_entry = tk.Entry(panel, show="*", font=FONT_NORMAL, width=30, relief="flat")
        self.pass_entry.pack(pady=(0, 20), ipady=5)

        tk.Button(panel, text="Login", font=FONT_NORMAL, bg=C_DARK_PURPLE, fg=C_WHITE, relief="flat",
                  command=self.do_login, cursor="hand2").pack(fill="x", ipady=5, pady=5)
        tk.Button(panel, text="Creează un cont nou", font=FONT_NORMAL, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE,
                  relief="flat", command=lambda: controller.show_frame("RegisterFrame"), cursor="hand2").pack(fill="x")

    def do_login(self):
        if self.controller.auth_service.login(self.email_entry.get(), self.pass_entry.get()):
            self.controller.show_frame("MainAppFrame")
        else:
            messagebox.showerror("Eroare", "Email sau parolă incorecte!")