import tkinter as tk
from tkinter import ttk, PhotoImage
from gui.tickets import cargar_tab_tickets, refrescar_tickets
from gui.ventas import cargar_tab_ventas, refrescar_ventas
from gui.inventario import cargar_tab_inventario, refrescar_inventario
from gui.usuarios import cargar_tab_usuarios, refrescar_usuarios
from gui.clientes import cargar_tab_clientes, refrescar_clientes

class MainWindow(tk.Toplevel):
    def __init__(self, master, username, rol):
        super().__init__(master)
        self.master = master
        self.title(f"NovaFix - Bienvenido {username} ({rol})")

        try:
            self.state("zoomed")
        except:
            self.attributes("-zoomed", True)

        self.configure(bg="white")
        tab = ttk.Notebook(self)

        self.tabs = {}

        # Clientes
        self.tabs["clientes"] = ttk.Frame(tab)
        tab.add(self.tabs["clientes"], text="Clientes")
        cargar_tab_clientes(self.tabs["clientes"])

        # Tickets
        self.tabs["tickets"] = ttk.Frame(tab)
        tab.add(self.tabs["tickets"], text="Tickets")
        cargar_tab_tickets(self.tabs["tickets"])

        # Ventas
        self.tabs["ventas"] = ttk.Frame(tab)
        tab.add(self.tabs["ventas"], text="Ventas")
        cargar_tab_ventas(self.tabs["ventas"])

        # Inventario (tecnico/sistemas)
        if rol in ("tecnico", "sistemas"):
            self.tabs["inventario"] = ttk.Frame(tab)
            tab.add(self.tabs["inventario"], text="Inventario")
            cargar_tab_inventario(self.tabs["inventario"])

        # Usuarios (solo sistemas)
        if rol == "sistemas":
            self.tabs["usuarios"] = ttk.Frame(tab)
            tab.add(self.tabs["usuarios"], text="Usuarios")
            cargar_tab_usuarios(self.tabs["usuarios"])

        tab.pack(expand=True, fill="both", padx=10, pady=10)

        # 🔹 refrescar al cambiar de pestaña
        def refrescar(_evt=None):
            current = tab.tab(tab.select(), "text")
            if current == "Clientes": refrescar_clientes()
            elif current == "Tickets": refrescar_tickets()
            elif current == "Ventas": refrescar_ventas()
            elif current == "Inventario": refrescar_inventario()
            elif current == "Usuarios": refrescar_usuarios()

        tab.bind("<<NotebookTabChanged>>", refrescar)
        self.master.withdraw()
