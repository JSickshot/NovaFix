import tkinter as tk
from tkinter import messagebox
import sqlite3
from database import DB
from gui.main_window import MainWindow

class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("NovaFix - Login")

        # 🔹 Tamaño fijo de la ventana
        w, h = 300, 180
        # 🔹 Tamaño de pantalla
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        # 🔹 Coordenadas para centrar
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))

        # Ajustar ventana
        self.master.geometry(f"{w}x{h}+{x}+{y}")
        self.master.resizable(False, False)

        # Formulario
        tk.Label(master, text="Usuario:").pack(pady=5)
        self.e_user = tk.Entry(master)
        self.e_user.pack(pady=5)

        tk.Label(master, text="Contraseña:").pack(pady=5)
        self.e_pass = tk.Entry(master, show="*")
        self.e_pass.pack(pady=5)

        tk.Button(master, text="Ingresar", command=self.check_login).pack(pady=10)

    def check_login(self):
        user = self.e_user.get().strip()
        pwd = self.e_pass.get().strip()

        if not user or not pwd:
            return messagebox.showerror("Error", "Ingresa usuario y contraseña")

        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("SELECT rol FROM usuarios WHERE username=? AND password=?", (user, pwd))
        row = c.fetchone()
        conn.close()

        if row:
            MainWindow(self.master, user, row[0])  # abrir ventana principal
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
