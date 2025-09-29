import tkinter as tk
from tkinter import messagebox
import sqlite3, os
from database import DB
from gui.main_window import MainWindow

class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("NovaFix - Login")

        w, h = 420, 320
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))
        self.master.geometry(f"{w}x{h}+{x}+{y}")
        self.master.resizable(False, False)
        self.master.configure(bg="black")

        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Novafix.png")
        try:
            self.logo = tk.PhotoImage(file=logo_path)
            tk.Label(master, image=self.logo, bg="black").pack(pady=10)
        except Exception:
            tk.Label(master, text="NovaFix", font=("Segoe UI", 20, "bold"),
                     fg="#BD181E", bg="black").pack(pady=10)

        form = tk.Frame(master, bg="black")
        form.pack(pady=10)

        tk.Label(form, text="Usuario:", font=("Segoe UI", 12, "bold"),
                 bg="black", fg="#DAA621").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.e_user = tk.Entry(form, font=("Segoe UI", 11), fg="white", bg="#222222",
                               insertbackground="white", bd=2, relief="flat")
        self.e_user.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form, text="Contraseña:", font=("Segoe UI", 12, "bold"),
                 bg="black", fg="#DAA621").grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.e_pass = tk.Entry(form, show="*", font=("Segoe UI", 11), fg="white", bg="#222222",
                               insertbackground="white", bd=2, relief="flat")
        self.e_pass.grid(row=1, column=1, pady=5, padx=5)

        btn = tk.Button(master, text="Ingresar", command=self.check_login,
                        bg="#BD181E", fg="white", font=("Segoe UI", 12, "bold"),
                        relief="flat", padx=20, pady=8, activebackground="#BD181E", activeforeground="black")
        btn.pack(pady=15)

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
            MainWindow(self.master, user, row[0])  # abre ventana principal
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
