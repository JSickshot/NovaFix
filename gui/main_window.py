import tkinter as tk
from tkinter import ttk
from gui.tickets import cargar_tab_tickets
from gui.inventario import cargar_tab_inventario

class MainWindow(tk.Toplevel):
    def __init__(self, master, username, rol):
        super().__init__(master)
        self.master = master  # para poder referenciar la ventana login si quieres
        self.title(f"NovaFix - Bienvenido {username} ({rol})")
        self.geometry("700x500")
        self.resizable(False, False)

        tabControl = ttk.Notebook(self)
        self.tab_tickets = ttk.Frame(tabControl)
        self.tab_inventario = ttk.Frame(tabControl)

        tabControl.add(self.tab_tickets, text='Tickets')
        tabControl.add(self.tab_inventario, text='Inventario')
        tabControl.pack(expand=1, fill="both")

        # Cargar contenidos de cada tab
        cargar_tab_tickets(self.tab_tickets)
        cargar_tab_inventario(self.tab_inventario)

        # Opcional: cerrar login al abrir MainWindow
        self.master.withdraw()
