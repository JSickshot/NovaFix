import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

DB = "novafix_pos.db"

# --- Funciones generales ---
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

# --- Tab de tickets ---
def cargar_tab_tickets(frame):
    # Formulario
    form_frame = ttk.LabelFrame(frame, text="Registrar Ticket")
    form_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky='w')
    entry_cliente = tk.Entry(form_frame, width=30)
    entry_cliente.grid(row=0, column=1, sticky='w')

    tk.Label(form_frame, text="Teléfono:").grid(row=0, column=2, sticky='w')
    entry_telefono = tk.Entry(form_frame, width=20)
    entry_telefono.grid(row=0, column=3, sticky='w')

    tk.Label(form_frame, text="Equipo:").grid(row=1, column=0, sticky='w')
    entry_equipo = tk.Entry(form_frame, width=30)
    entry_equipo.grid(row=1, column=1, sticky='w')

    tk.Label(form_frame, text="Falla reportada:").grid(row=2, column=0, sticky='w')
    entry_falla = tk.Entry(form_frame, width=50)
    entry_falla.grid(row=2, column=1, columnspan=3, sticky='w')

    tk.Label(form_frame, text="Estado:").grid(row=3, column=0, sticky='w')
    combo_estado = ttk.Combobox(form_frame, values=["Pendiente", "En reparación", "Terminado", "Entregado"], state="readonly")
    combo_estado.current(0)
    combo_estado.grid(row=3, column=1, sticky='w')

    tk.Label(form_frame, text="Fecha entrega (dd/mm/aaaa):").grid(row=3, column=2, sticky='w')
    entry_fecha_entrega = tk.Entry(form_frame, width=20)
    entry_fecha_entrega.grid(row=3, column=3, sticky='w')

    # Treeview
    tree_tickets = ttk.Treeview(frame, columns=("folio", "cliente", "equipo", "estado", "fecha_ingreso", "fecha_entrega"), show='headings')
    tree_tickets.heading("folio", text="Folio")
    tree_tickets.heading("cliente", text="Cliente")
    tree_tickets.heading("equipo", text="Equipo")
    tree_tickets.heading("estado", text="Estado")
    tree_tickets.heading("fecha_ingreso", text="Ingreso")
    tree_tickets.heading("fecha_entrega", text="Entrega")
    tree_tickets.pack(fill='both', expand=True, padx=10, pady=5)

    # --- Funciones internas ---
    def cargar_tickets_tree():
        for row in tree_tickets.get_children():
            tree_tickets.delete(row)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT folio, cliente, equipo, estado, fecha_ingreso, fecha_entrega FROM tickets ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            tree_tickets.insert("", tk.END, values=row)

    def guardar_ticket():
        cliente = entry_cliente.get().strip()
        telefono = entry_telefono.get().strip()
        equipo = entry_equipo.get().strip()
        falla = entry_falla.get().strip()
        estado = combo_estado.get()
        fecha_entrega = entry_fecha_entrega.get().strip()

        if not cliente or not equipo or not falla:
            messagebox.showerror("Error", "Debe llenar Cliente, Equipo y Falla.")
            return
        if fecha_entrega:
            try:
                datetime.strptime(fecha_entrega, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use dd/mm/aaaa.")
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
        cargar_tickets_tree()
        exportar_ticket_pdf(folio)  # Guarda PDF automáticamente al crear

    def cambiar_estado():
        sel = tree_tickets.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un ticket primero")
            return
        item = tree_tickets.item(sel[0])
        folio = item["values"][0]
        nuevo_estado = simpledialog.askstring("Cambiar Estado", "Nuevo estado (Pendiente, En reparación, Terminado, Entregado):")
        if nuevo_estado not in ["Pendiente", "En reparación", "Terminado", "Entregado"]:
            messagebox.showerror("Error", "Estado inválido")
            return
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("UPDATE tickets SET estado=? WHERE folio=?", (nuevo_estado, folio))
        conn.commit()
        conn.close()
        cargar_tickets_tree()
        messagebox.showinfo("Éxito", f"Estado del ticket {folio} actualizado a {nuevo_estado}")

    def exportar_seleccion():
        sel = tree_tickets.selection()
        if sel:
            folio = tree_tickets.item(sel[0], "values")[0]
            exportar_ticket_pdf(folio)
        else:
            messagebox.showwarning("Atención", "Seleccione un ticket primero")

    # --- Botones ---
    tk.Button(form_frame, text="Guardar Ticket y Exportar PDF", command=guardar_ticket).grid(row=4, column=0, pady=10)
    tk.Button(frame, text="Cambiar Estado Ticket Seleccionado", command=cambiar_estado).pack(pady=5)
    tk.Button(frame, text="Exportar Ticket Seleccionado a PDF", command=exportar_seleccion).pack(pady=5)

    cargar_tickets_tree()
