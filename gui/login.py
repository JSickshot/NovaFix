import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB
from gui.main_window import MainWindow

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - NovaFix")
        self.geometry("300x200")
        self.resizable(False, False)

        ttk.Label(self, text="Usuario:").pack(pady=5)
        self.entry_user = ttk.Entry(self)
        self.entry_user.pack()

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_pass = ttk.Entry(self, show="*")
        self.entry_pass.pack()

        ttk.Button(self, text="Ingresar", command=self.check_login).pack(pady=10)

    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT rol FROM usuarios WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        conn.close()

        if row:
            # Abrir ventana principal usando Toplevel
            MainWindow(self, username, row[0])
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
