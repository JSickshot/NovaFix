import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from database import DB
from gui.inventario import refrescar_inventario

tree_ventas = None
cb_cliente = None
cb_pieza = None

def _get_clientes():
    conn=sqlite3.connect(DB);c=conn.cursor()
    c.execute("SELECT cliente_id,nombre FROM clientes ORDER BY nombre")
    rows=c.fetchall();conn.close();return rows

def _get_piezas():
    conn=sqlite3.connect(DB);c=conn.cursor()
    c.execute("SELECT pieza_id,pieza,stock,precio_unitario FROM inventario ORDER BY pieza")
    rows=c.fetchall();conn.close();return rows

def _exportar_comprobante(cliente,ventas,total):
    pdf_file=f"Venta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c=canvas.Canvas(pdf_file,pagesize=letter)
    c.setFont("Helvetica-Bold",18);c.setFillColor(colors.HexColor("#2980B9"))
    c.drawCentredString(300,770,"NOVA FIX - COMPROBANTE DE VENTA")
    c.setFillColor(colors.black);c.setFont("Helvetica",12)
    c.drawString(50,740,f"Cliente: {cliente['nombre']}");c.drawString(400,740,f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(50,720,f"Dirección: {cliente['direccion'] or 'N/D'}")
    c.drawString(50,705,f"Ciudad: {cliente['ciudad'] or 'N/D'}   CP: {cliente['cp'] or 'N/D'}")
    y=680;c.setFont("Helvetica-Bold",11)
    c.drawString(50,y,"Pieza");c.drawString(250,y,"Cantidad");c.drawString(330,y,"Precio U.");c.drawString(420,y,"Importe")
    c.setFont("Helvetica",11)
    for pieza,cant,precio,importe in ventas:
        y-=20;c.drawString(50,y,pieza);c.drawString(250,y,str(cant));c.drawString(330,y,f"${precio:.2f}");c.drawString(420,y,f"${importe:.2f}")
    y-=30;c.setFont("Helvetica-Bold",12);c.drawString(330,y,"TOTAL:");c.drawString(420,y,f"${total:.2f}")
    c.save()
    try: os.startfile(pdf_file)
    except: pass
    messagebox.showinfo("PDF",f"Se generó: {pdf_file}")

def cargar_tab_ventas(frame):
    global tree_ventas, cb_cliente, cb_pieza

    form=ttk.LabelFrame(frame,text="Registrar Venta");form.pack(fill="x",padx=10,pady=10)
    cb_cliente=ttk.Combobox(form,state="readonly",width=30)
    cb_pieza=ttk.Combobox(form,state="readonly",width=30)
    e_cant=tk.Entry(form,width=8)

    tk.Label(form,text="Cliente:").grid(row=0,column=0);cb_cliente.grid(row=0,column=1)
    tk.Label(form,text="Pieza:").grid(row=1,column=0);cb_pieza.grid(row=1,column=1)
    tk.Label(form,text="Cantidad:").grid(row=1,column=2);e_cant.grid(row=1,column=3)

    def cargar_combos():
        cb_cliente["values"]=[f"{cid}:{nom}" for cid,nom in _get_clientes()]
        cb_pieza["values"]=[f"{pid}:{nom} (stk {stk}) ${precio}" for pid,nom,stk,precio in _get_piezas()]
    cargar_combos()

    tree_ventas=ttk.Treeview(frame,columns=("venta_id","cliente","pieza","cantidad","precio","importe"),show="headings")
    for c in ("venta_id","cliente","pieza","cantidad","precio","importe"):tree_ventas.heading(c,text=c.capitalize())
    tree_ventas.pack(fill="both",expand=True,padx=10,pady=5)
    ventas_actual=[]

    def agregar():
        if not cb_pieza.get():return
        pid=int(cb_pieza.get().split(":")[0]);cant=int(e_cant.get())
        conn=sqlite3.connect(DB);c=conn.cursor();c.execute("SELECT pieza,stock,precio_unitario FROM inventario WHERE pieza_id=?",(pid,))
        row=c.fetchone();conn.close()
        if not row:return
        pieza,stk,precio=row
        if cant>stk:return messagebox.showerror("Error","Stock insuficiente")
        importe=cant*precio;ventas_actual.append((pid,pieza,cant,precio,importe))
        tree_ventas.insert("",tk.END,values=(None,"",pieza,cant,precio,importe))

    def finalizar():
        if not cb_cliente.get():return messagebox.showerror("Error","Selecciona cliente")
        cliente_id=int(cb_cliente.get().split(":")[0])
        if not ventas_actual:return messagebox.showerror("Error","Sin productos")
        folio=f"VEN-{datetime.now().strftime('%H%M%S')}";fecha=datetime.now().strftime("%Y-%m-%d %H:%M")
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("INSERT INTO tickets (folio,cliente_id,fecha_ingreso,descripcion_equipo,diagnostico,estado,costo_total) VALUES (?,?,?,?,?,?,?)",
                  (folio,cliente_id,fecha,"VENTA DIRECTA","N/A","Entregado",sum(v[4] for v in ventas_actual)))
        tid=c.lastrowid
        for pid,pieza,cant,precio,importe in ventas_actual:
            c.execute("INSERT INTO ventas (ticket_id,pieza_id,cantidad,precio_unitario) VALUES (?,?,?,?)",(tid,pid,cant,precio))
            c.execute("UPDATE inventario SET stock=stock-? WHERE pieza_id=?",(cant,pid))
        c.execute("SELECT nombre,direccion,ciudad,codigo_postal FROM clientes WHERE cliente_id=?",(cliente_id,))
        row=c.fetchone();conn.commit();conn.close()
        cliente=dict(nombre=row[0],direccion=row[1],ciudad=row[2],cp=row[3])
        detalle=[(v[1],v[2],v[3],v[4]) for v in ventas_actual];total=sum(v[4] for v in ventas_actual)
        _exportar_comprobante(cliente,detalle,total)
        ventas_actual.clear();tree_ventas.delete(*tree_ventas.get_children());cargar_combos();cargar_tabla();refrescar_inventario()

    ttk.Button(form,text="Agregar",command=agregar).grid(row=1,column=4);ttk.Button(form,text="Finalizar",command=finalizar).grid(row=1,column=5)

    def cargar_tabla():
        tree_ventas.delete(*tree_ventas.get_children())
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("""SELECT v.venta_id,c.nombre,i.pieza,v.cantidad,v.precio_unitario,(v.cantidad*v.precio_unitario)
                     FROM ventas v JOIN tickets t ON v.ticket_id=t.ticket_id
                     JOIN clientes c ON t.cliente_id=c.cliente_id
                     JOIN inventario i ON v.pieza_id=i.pieza_id ORDER BY v.venta_id DESC""")
        for row in c.fetchall():tree_ventas.insert("",tk.END,values=row)
        conn.close()

    def editar_venta(_evt=None):
        sel=tree_ventas.selection()
        if not sel:return
        vals=tree_ventas.item(sel[0])["values"];vid=vals[0]
        win=tk.Toplevel(frame);win.title("Editar Venta")
        e_cant=tk.Entry(win);e_cant.insert(0,vals[3]);e_cant.grid(row=0,column=1);tk.Label(win,text="Cantidad").grid(row=0,column=0)
        def guardar():
            nueva=int(e_cant.get());conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("UPDATE ventas SET cantidad=? WHERE venta_id=?",(nueva,vid))
            conn.commit();conn.close();cargar_tabla();refrescar_inventario();win.destroy()
        tk.Button(win,text="Guardar",command=guardar).grid(row=1,column=0,columnspan=2)
    tree_ventas.bind("<Double-1>",editar_venta)
    cargar_tabla()

def refrescar_ventas():
    try:
        if tree_ventas:
            tree_ventas.delete(*tree_ventas.get_children())
            conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("""SELECT v.venta_id,c.nombre,i.pieza,v.cantidad,v.precio_unitario,(v.cantidad*v.precio_unitario)
                         FROM ventas v JOIN tickets t ON v.ticket_id=t.ticket_id
                         JOIN clientes c ON t.cliente_id=c.cliente_id
                         JOIN inventario i ON v.pieza_id=i.pieza_id ORDER BY v.venta_id DESC""")
            for row in c.fetchall():tree_ventas.insert("",tk.END,values=row)
            conn.close()
        if cb_cliente:
            cb_cliente["values"]=[f"{cid}:{nom}" for cid,nom in _get_clientes()]
        if cb_pieza:
            cb_pieza["values"]=[f"{pid}:{nom} (stk {stk}) ${precio}" for pid,nom,stk,precio in _get_piezas()]
    except Exception as e:
        print("Error refrescando ventas:", e)
