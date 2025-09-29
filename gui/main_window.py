import tkinter as tk
from tkinter import ttk, PhotoImage
from gui.tickets import cargar_tab_tickets, refrescar_tickets
from gui.ventas import cargar_tab_ventas, refrescar_ventas
from gui.inventario import cargar_tab_inventario, refrescar_inventario
from gui.usuarios import cargar_tab_usuarios, refrescar_usuarios
from gui.clientes import cargar_tab_clientes, refrescar_clientes
import os

def aplicar_estilo():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TNotebook", background="black", borderwidth=0)
    style.configure("TNotebook.Tab",
                    font=("Segoe UI", 11, "bold"),
                    background="#BD181E",
                    foreground="white",
                    padding=[15, 8])
    style.map("TNotebook.Tab",
              background=[("selected", "#F1C40F")],
              foreground=[("selected", "black")])

    style.configure("Treeview",
                    background="#1E1E1E",
                    foreground="white",
                    rowheight=26,
                    fieldbackground="#1E1E1E",
                    borderwidth=0,
                    font=("Segoe UI", 10))
    style.map("Treeview",
              background=[("selected", "#E30613")],
              foreground=[("selected", "white")])

    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    background="#F1C40F",
                    foreground="black")

    style.configure("Custom.TButton",
                    font=("Segoe UI", 11, "bold"),
                    background="#E30613",
                    foreground="white",
                    padding=6)
    style.map("Custom.TButton",
              background=[("active", "#F1C40F")],
              foreground=[("active", "black")])

class MainWindow(tk.Toplevel):
    def __init__(self, master, username, rol):
        super().__init__(master)
        self.master = master
        self.title(f"NovaFix - Bienvenido {username} ({rol})")

        try:
            self.state("zoomed")
        except Exception:
            self.attributes("-zoomed", True)

        self.configure(bg="black")
        aplicar_estilo()

        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Novafix.png")
        try:
            self.logo = PhotoImage(file=logo_path)
            tk.Label(self, image=self.logo, bg="black").pack(pady=10)
        except Exception:
            tk.Label(self, text="NovaFix", font=("Segoe UI", 22, "bold"),
                     fg="#DAA621", bg="black").pack(pady=10)

        tabControl = ttk.Notebook(self)

        self.tab_clientes = ttk.Frame(tabControl, style="TNotebook")
        tabControl.add(self.tab_clientes, text="Clientes")
        cargar_tab_clientes(self.tab_clientes)

        self.tab_tickets = ttk.Frame(tabControl, style="TNotebook")
        tabControl.add(self.tab_tickets, text="Tickets")
        cargar_tab_tickets(self.tab_tickets)

        self.tab_ventas = ttk.Frame(tabControl, style="TNotebook")
        tabControl.add(self.tab_ventas, text="Ventas")
        cargar_tab_ventas(self.tab_ventas)

        if rol in ("tecnico", "sistemas"):
            self.tab_inventario = ttk.Frame(tabControl, style="TNotebook")
            tabControl.add(self.tab_inventario, text="Inventario")
            cargar_tab_inventario(self.tab_inventario)

        if rol == "sistemas":
            self.tab_usuarios = ttk.Frame(tabControl, style="TNotebook")
            tabControl.add(self.tab_usuarios, text="Usuarios")
            cargar_tab_usuarios(self.tab_usuarios)

        tabControl.pack(expand=True, fill="both", padx=10, pady=10)

        def refrescar(_evt=None):
            current = tabControl.tab(tabControl.select(), "text")
            if current == "Clientes": refrescar_clientes()
            elif current == "Tickets": refrescar_tickets()
            elif current == "Ventas": refrescar_ventas()
            elif current == "Inventario": refrescar_inventario()
            elif current == "Usuarios": refrescar_usuarios()

        tabControl.bind("<<NotebookTabChanged>>", refrescar)

        self.master.withdraw()
