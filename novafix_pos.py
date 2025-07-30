import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

DB = 'novafix_pos.db'

def crear_tablas():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE,
        cliente TEXT,
        telefono TEXT,
        equipo TEXT,
        falla TEXT,
        estado TEXT,
        fecha_ingreso TEXT,
        fecha_entrega TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pieza TEXT UNIQUE,
        descripcion TEXT,
        stock INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def generar_folio():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT folio FROM tickets ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        last_folio = row[0]
        num = int(last_folio.split('-')[1]) + 1
    else:
        num = 1
    return f"TCK-{num:04d}"

def exportar_ticket_pdf(folio):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE folio = ?", (folio,))
    ticket = c.fetchone()
    conn.close()

    if not ticket:
        messagebox.showerror("Error", "No se encontró el ticket.")
        return

    _, folio, cliente, telefono, equipo, falla, estado, fecha_ingreso, fecha_entrega = ticket
    pdf_file = f"{folio}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "TICKET DE SERVICIO - NOVA FIX")
    c.setFont("Helvetica", 12)

    c.drawString(50, 720, f"Folio: {folio}")
    c.drawString(300, 720, f"Fecha Ingreso: {fecha_ingreso}")
    c.drawString(50, 700, f"Cliente: {cliente}")
    c.drawString(300, 700, f"Teléfono: {telefono}")
    c.drawString(50, 680, f"Equipo: {equipo}")
    c.drawString(50, 660, f"Falla reportada: {falla}")
    c.drawString(50, 640, f"Estado: {estado}")
    c.drawString(300, 640, f"Entrega estimada: {fecha_entrega}")
    c.drawString(50, 580, "Firma cliente: _________________________________")
    c.save()
    messagebox.showinfo("Éxito", f"Ticket exportado como {pdf_file}")
    os.startfile(pdf_file)


class NovaFixPOS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pos")
        self.geometry("700x500")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        tabControl = ttk.Notebook(self)
        self.tab_tickets = ttk.Frame(tabControl)
        self.tab_inventario = ttk.Frame(tabControl)

        tabControl.add(self.tab_tickets, text='Tickets')
        tabControl.add(self.tab_inventario, text='Inventario')
        tabControl.pack(expand=1, fill="both")

        # Tickets Tab
        self.frame_ticket_form = ttk.LabelFrame(self.tab_tickets, text="Registrar Ticket")
        self.frame_ticket_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(self.frame_ticket_form, text="Cliente:").grid(row=0, column=0, sticky='w')
        self.entry_cliente = ttk.Entry(self.frame_ticket_form, width=30)
        self.entry_cliente.grid(row=0, column=1, sticky='w')

        ttk.Label(self.frame_ticket_form, text="Teléfono:").grid(row=0, column=2, sticky='w')
        self.entry_telefono = ttk.Entry(self.frame_ticket_form, width=20)
        self.entry_telefono.grid(row=0, column=3, sticky='w')

        ttk.Label(self.frame_ticket_form, text="Equipo:").grid(row=1, column=0, sticky='w')
        self.entry_equipo = ttk.Entry(self.frame_ticket_form, width=30)
        self.entry_equipo.grid(row=1, column=1, sticky='w')

        ttk.Label(self.frame_ticket_form, text="Falla reportada:").grid(row=2, column=0, sticky='w')
        self.entry_falla = ttk.Entry(self.frame_ticket_form, width=50)
        self.entry_falla.grid(row=2, column=1, columnspan=3, sticky='w')

        ttk.Label(self.frame_ticket_form, text="Estado:").grid(row=3, column=0, sticky='w')
        self.combo_estado = ttk.Combobox(self.frame_ticket_form, values=["Pendiente", "En reparación", "Terminado", "Entregado"], state="readonly")
        self.combo_estado.current(0)
        self.combo_estado.grid(row=3, column=1, sticky='w')

        ttk.Label(self.frame_ticket_form, text="Fecha entrega (dd/mm/aaaa):").grid(row=3, column=2, sticky='w')
        self.entry_fecha_entrega = ttk.Entry(self.frame_ticket_form, width=20)
        self.entry_fecha_entrega.grid(row=3, column=3, sticky='w')

        ttk.Button(self.frame_ticket_form, text="Guardar Ticket", command=self.guardar_ticket).grid(row=4, column=0, pady=10)

        ttk.Separator(self.tab_tickets, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # Lista tickets
        self.tree_tickets = ttk.Treeview(self.tab_tickets, columns=("folio", "cliente", "equipo", "estado", "fecha_ingreso", "fecha_entrega"), show='headings')
        self.tree_tickets.heading("folio", text="Folio")
        self.tree_tickets.heading("cliente", text="Cliente")
        self.tree_tickets.heading("equipo", text="Equipo")
        self.tree_tickets.heading("estado", text="Estado")
        self.tree_tickets.heading("fecha_ingreso", text="Ingreso")
        self.tree_tickets.heading("fecha_entrega", text="Entrega")
        self.tree_tickets.pack(fill='both', expand=True, padx=10, pady=5)

        self.cargar_tickets()

        # Inventario Tab
        self.frame_inv_form = ttk.LabelFrame(self.tab_inventario, text="Agregar / Editar Pieza")
        self.frame_inv_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(self.frame_inv_form, text="Pieza:").grid(row=0, column=0, sticky='w')
        self.entry_pieza = ttk.Entry(self.frame_inv_form, width=30)
        self.entry_pieza.grid(row=0, column=1, sticky='w')

        ttk.Label(self.frame_inv_form, text="Descripción:").grid(row=1, column=0, sticky='w')
        self.entry_descripcion = ttk.Entry(self.frame_inv_form, width=50)
        self.entry_descripcion.grid(row=1, column=1, sticky='w')

        ttk.Label(self.frame_inv_form, text="Stock:").grid(row=2, column=0, sticky='w')
        self.entry_stock = ttk.Entry(self.frame_inv_form, width=10)
        self.entry_stock.grid(row=2, column=1, sticky='w')

        ttk.Button(self.frame_inv_form, text="Guardar Pieza", command=self.guardar_pieza).grid(row=3, column=0, pady=10)

        ttk.Separator(self.tab_inventario, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # Lista inventario
        self.tree_inventario = ttk.Treeview(self.tab_inventario, columns=("pieza", "descripcion", "stock"), show='headings')
        self.tree_inventario.heading("pieza", text="Pieza")
        self.tree_inventario.heading("descripcion", text="Descripción")
        self.tree_inventario.heading("stock", text="Stock")
        self.tree_inventario.pack(fill='both', expand=True, padx=10, pady=5)

        self.cargar_inventario()

    def guardar_ticket(self):
        cliente = self.entry_cliente.get().strip()
        telefono = self.entry_telefono.get().strip()
        equipo = self.entry_equipo.get().strip()
        falla = self.entry_falla.get().strip()
        estado = self.combo_estado.get()
        fecha_entrega = self.entry_fecha_entrega.get().strip()
        if not cliente or not equipo or not falla:
            messagebox.showerror("Error", "Debe llenar los campos: Cliente, Equipo y Falla.")
            return
        if fecha_entrega:
            try:
                datetime.strptime(fecha_entrega, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de entrega inválido. Use dd/mm/aaaa.")
                return
        folio = generar_folio()
        fecha_ingreso = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''
            INSERT INTO tickets(folio, cliente, telefono, equipo, falla, estado, fecha_ingreso, fecha_entrega)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (folio, cliente, telefono, equipo, falla, estado, fecha_ingreso, fecha_entrega))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", f"Ticket guardado con folio {folio}")
        self.limpiar_form_ticket()
        self.cargar_tickets()

    def limpiar_form_ticket(self):
        self.entry_cliente.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_equipo.delete(0, tk.END)
        self.entry_falla.delete(0, tk.END)
        self.combo_estado.current(0)
        self.entry_fecha_entrega.delete(0, tk.END)

    def cargar_tickets(self):
        for row in self.tree_tickets.get_children():
            self.tree_tickets.delete(row)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT folio, cliente, equipo, estado, fecha_ingreso, fecha_entrega FROM tickets ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self.tree_tickets.insert("", tk.END, values=row)

    def guardar_pieza(self):
        pieza = self.entry_pieza.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        stock = self.entry_stock.get().strip()
        if not pieza or not stock:
            messagebox.showerror("Error", "Debe llenar los campos: Pieza y Stock.")
            return
        try:
            stock_int = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Stock debe ser un número entero.")
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT id FROM inventario WHERE pieza = ?", (pieza,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE inventario SET descripcion=?, stock=? WHERE id=?", (descripcion, stock_int, row[0]))
        else:
            c.execute("INSERT INTO inventario(pieza, descripcion, stock) VALUES (?, ?, ?)", (pieza, descripcion, stock_int))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", f"Pieza '{pieza}' guardada.")
        self.limpiar_form_inventario()
        self.cargar_inventario()

    def limpiar_form_inventario(self):
        self.entry_pieza.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)

    def cargar_inventario(self):
        for row in self.tree_inventario.get_children():
            self.tree_inventario.delete(row)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT pieza, descripcion, stock FROM inventario ORDER BY pieza")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self.tree_inventario.insert("", tk.END, values=row)
    

if __name__ == "__main__":
    crear_tablas()
    app = NovaFixPOS()
    app.mainloop()
