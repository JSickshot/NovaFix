import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB
from gui.main_window import MainWindow

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - NovaFix")
        self.geometry("340x210")
        self.resizable(False, False)

        ttk.Label(self, text="Usuario:").pack(pady=(14,4))
        self.entry_user = ttk.Entry(self, width=26)
        self.entry_user.pack()

        ttk.Label(self, text="Contraseña:").pack(pady=(10,4))
        self.entry_pass = ttk.Entry(self, show="*", width=26)
        self.entry_pass.pack()

        ttk.Button(self, text="Ingresar", command=self.check_login).pack(pady=14)

    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT rol FROM usuarios WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()

        if row:
            MainWindow(self, username, row[0])
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
