# register_page.py
import tkinter as tk
from tkinter import messagebox
from config import *


class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=C_DARK_PURPLE)
        self.controller = controller

        panel = tk.Frame(self, bg=C_LIGHT_PURPLE, padx=40, pady=40)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(panel, text="Cont Nou", font=FONT_TITLE, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE).pack(pady=(0, 20))

        self.entries = {}
        for field in ["Nume", "Email", "Parola"]:
            tk.Label(panel, text=field, font=FONT_NORMAL, bg=C_LIGHT_PURPLE).pack(anchor="w")
            e = tk.Entry(panel, show="*" if field == "Parola" else "", font=FONT_NORMAL, width=30, relief="flat")
            e.pack(pady=(0, 10), ipady=5)
            self.entries[field] = e

        tk.Button(panel, text="Înregistrare", font=FONT_NORMAL, bg=C_DARK_PURPLE, fg=C_WHITE, relief="flat",
                  command=self.do_register, cursor="hand2").pack(fill="x", ipady=5, pady=5)
        tk.Button(panel, text="Înapoi la Login", font=FONT_NORMAL, bg=C_LIGHT_PURPLE, fg=C_DARK_PURPLE, relief="flat",
                  command=lambda: controller.show_frame("LoginFrame"), cursor="hand2").pack(fill="x")

    def do_register(self):
        if self.controller.auth_service.register(self.entries["Nume"].get(), self.entries["Email"].get(),
                                                 self.entries["Parola"].get()):
            messagebox.showinfo("Succes", "Cont creat!")
            self.controller.show_frame("LoginFrame")
        else:
            messagebox.showerror("Eroare", "Emailul există deja!")