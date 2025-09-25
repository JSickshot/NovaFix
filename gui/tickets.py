import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib import colors
from database import DB

# variables globales
tree_tickets = None
combo_cliente = None

def _get_clientes():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT cliente_id, nombre FROM clientes ORDER BY nombre")
    rows = c.fetchall(); conn.close()
    return rows

def _generar_folio():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT folio FROM tickets ORDER BY ticket_id DESC LIMIT 1")
    row = c.fetchone(); conn.close()
    num = int(row[0].split('-')[1]) + 1 if row else 1
    return f"TCK-{num:04d}"

def _exportar_ticket_pdf(folio, datos):
    pdf_file = f"{folio}.pdf"
    c = pdfcanvas.Canvas(pdf_file, pagesize=letter)

    # Título
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(300, 770, "NOVA FIX - TICKET DE REPARACIÓN")

    # Encabezado
    c.setFont("Helvetica", 12)
    c.drawString(50, 740, f"Folio: {folio}")
    c.drawString(350, 740, f"Fecha: {datos['fecha_ingreso']}")

    # Cliente
    cli = datos["cliente"]
    c.setFont("Helvetica-Bold", 12); c.drawString(50, 710, "Datos del Cliente:")
    c.setFont("Helvetica", 11)
    c.drawString(70, 695, f"Nombre: {cli['nombre']}")
    c.drawString(70, 680, f"Teléfono: {cli['telefono'] or 'N/D'}")
    c.drawString(70, 665, f"Email: {cli['email'] or 'N/D'}")
    c.drawString(70, 650, f"Dirección: {cli['direccion'] or 'N/D'}")
    c.drawString(70, 635, f"Ciudad: {cli['ciudad'] or 'N/D'}")
    c.drawString(70, 620, f"CP: {cli['cp'] or 'N/D'}")

    # Equipo
    c.setFont("Helvetica-Bold", 12); c.drawString(50, 590, "Datos del Equipo:")
    c.setFont("Helvetica", 11)
    c.drawString(70, 575, f"Equipo: {datos['equipo']}")
    c.drawString(70, 560, f"Diagnóstico: {datos['diagnostico']}")
    c.drawString(70, 545, f"Estado: {datos['estado']}")
    c.drawString(70, 530, f"Anticipo: ${datos['anticipo']:.2f}")

    # Firma
    c.line(50, 500, 300, 500)
    c.drawString(50, 485, "Firma cliente")

    c.save()
    try: os.startfile(pdf_file)
    except: pass
    messagebox.showinfo("PDF", f"Ticket exportado como {pdf_file}")

def cargar_tab_tickets(frame):
    global tree_tickets, combo_cliente

    form = ttk.LabelFrame(frame, text="Generar Ticket")
    form.pack(fill="x", padx=10, pady=10)

    combo_cliente = ttk.Combobox(form, state="readonly", width=40)
    tk.Label(form, text="Cliente:").grid(row=0, column=0)
    combo_cliente.grid(row=0, column=1, columnspan=2, sticky="w")

    def cargar_combo_clientes():
        combo_cliente["values"] = [f"{cid} - {nom}" for cid, nom in _get_clientes()]
    cargar_combo_clientes()

    e_equipo = tk.Entry(form, width=40)
    e_diag = tk.Entry(form, width=60)
    e_anticipo = tk.Entry(form, width=15)
    combo_estado = ttk.Combobox(form, values=["Pendiente","En reparación","Terminado","Entregado"], state="readonly")
    combo_estado.current(0)

    tk.Label(form, text="Equipo:").grid(row=1, column=0); e_equipo.grid(row=1, column=1)
    tk.Label(form, text="Diagnóstico:").grid(row=2, column=0); e_diag.grid(row=2, column=1)
    tk.Label(form, text="Anticipo:").grid(row=3, column=0); e_anticipo.grid(row=3, column=1)
    tk.Label(form, text="Estado:").grid(row=4, column=0); combo_estado.grid(row=4, column=1)

    tree_tickets = ttk.Treeview(frame, columns=("ticket_id","folio","cliente","equipo","estado","fecha_ingreso","anticipo"), show="headings")
    for c in ("ticket_id","folio","cliente","equipo","estado","fecha_ingreso","anticipo"):
        tree_tickets.heading(c, text=c.capitalize())
    tree_tickets.pack(fill="both", expand=True, padx=10, pady=6)

    def cargar_tickets_tree():
        for r in tree_tickets.get_children(): tree_tickets.delete(r)
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("""SELECT t.ticket_id,t.folio,c.nombre,t.descripcion_equipo,t.estado,t.fecha_ingreso,t.anticipo
                     FROM tickets t LEFT JOIN clientes c ON t.cliente_id=c.cliente_id ORDER BY t.ticket_id DESC""")
        for row in c.fetchall(): tree_tickets.insert("", tk.END, values=row)
        conn.close()

    def guardar_ticket():
        if not combo_cliente.get(): return messagebox.showerror("Error","Selecciona cliente")
        cliente_id=int(combo_cliente.get().split(" - ")[0])
        folio=_generar_folio();fecha=datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            anticipo=float(e_anticipo.get()) if e_anticipo.get() else 0
        except: return messagebox.showerror("Error","Anticipo debe ser numérico")

        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("INSERT INTO tickets (folio,cliente_id,fecha_ingreso,descripcion_equipo,diagnostico,estado,anticipo) VALUES (?,?,?,?,?,?,?)",
                  (folio,cliente_id,fecha,e_equipo.get(),e_diag.get(),combo_estado.get(),anticipo))
        conn.commit()
        c.execute("SELECT nombre,telefono,email,direccion,ciudad,codigo_postal FROM clientes WHERE cliente_id=?",(cliente_id,))
        row=c.fetchone();conn.close()
        datos=dict(cliente=dict(nombre=row[0],telefono=row[1],email=row[2],direccion=row[3],ciudad=row[4],cp=row[5]),
                   equipo=e_equipo.get(),diagnostico=e_diag.get(),estado=combo_estado.get(),
                   fecha_ingreso=fecha,anticipo=anticipo)
        _exportar_ticket_pdf(folio,datos)
        cargar_tickets_tree();cargar_combo_clientes()

    ttk.Button(form,text="Guardar Ticket + PDF",command=guardar_ticket).grid(row=4,column=2)

    def editar_ticket(_evt=None):
        sel=tree_tickets.selection()
        if not sel:return
        vals=tree_tickets.item(sel[0])["values"];tid=vals[0]
        win=tk.Toplevel(frame);win.title("Editar Ticket")
        e_equipo=tk.Entry(win);e_equipo.insert(0,vals[3]);e_equipo.grid(row=0,column=1);tk.Label(win,text="Equipo").grid(row=0,column=0)
        e_estado=tk.Entry(win);e_estado.insert(0,vals[4]);e_estado.grid(row=1,column=1);tk.Label(win,text="Estado").grid(row=1,column=0)
        e_antic=tk.Entry(win);e_antic.insert(0,vals[6]);e_antic.grid(row=2,column=1);tk.Label(win,text="Anticipo").grid(row=2,column=0)
        def guardar():
            try: nuevo=float(e_antic.get())
            except: return messagebox.showerror("Error","Anticipo debe ser numérico")
            conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("UPDATE tickets SET descripcion_equipo=?,estado=?,anticipo=? WHERE ticket_id=?",
                      (e_equipo.get(),e_estado.get(),nuevo,tid))
            conn.commit();conn.close();cargar_tickets_tree();win.destroy()
        tk.Button(win,text="Guardar",command=guardar).grid(row=3,column=0,columnspan=2)
    tree_tickets.bind("<Double-1>",editar_ticket)
    cargar_tickets_tree()

def refrescar_tickets():
    try:
        if tree_tickets:
            for r in tree_tickets.get_children(): tree_tickets.delete(r)
            conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("""SELECT t.ticket_id,t.folio,c.nombre,t.descripcion_equipo,t.estado,t.fecha_ingreso,t.anticipo
                         FROM tickets t LEFT JOIN clientes c ON t.cliente_id=c.cliente_id ORDER BY t.ticket_id DESC""")
            for row in c.fetchall(): tree_tickets.insert("", tk.END, values=row)
            conn.close()
        if combo_cliente:
            combo_cliente["values"] = [f"{cid} - {nom}" for cid, nom in _get_clientes()]
    except Exception as e:
        print("Error refrescando tickets:", e)
