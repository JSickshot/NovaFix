import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import DB

def cargar_tab_clientes(frame):
    global tree_clientes, cargar_listado

    form = ttk.LabelFrame(frame, text="Alta Cliente")
    form.pack(fill="x", padx=10, pady=10)

    e_nombre = tk.Entry(form, width=24)
    e_apellido = tk.Entry(form, width=24)
    e_tel = tk.Entry(form, width=20)
    e_email = tk.Entry(form, width=28)
    e_dir = tk.Entry(form, width=48)
    e_ciudad = tk.Entry(form, width=24)
    e_cp = tk.Entry(form, width=10)

    tk.Label(form, text="Nombre:").grid(row=0, column=0); e_nombre.grid(row=0, column=1)
    tk.Label(form, text="Apellido:").grid(row=0, column=2); e_apellido.grid(row=0, column=3)
    tk.Label(form, text="Teléfono:").grid(row=1, column=0); e_tel.grid(row=1, column=1)
    tk.Label(form, text="Email:").grid(row=1, column=2); e_email.grid(row=1, column=3)
    tk.Label(form, text="Dirección:").grid(row=2, column=0); e_dir.grid(row=2, column=1, columnspan=3, sticky="we")
    tk.Label(form, text="Ciudad:").grid(row=3, column=0); e_ciudad.grid(row=3, column=1)
    tk.Label(form, text="CP:").grid(row=3, column=2); e_cp.grid(row=3, column=3)

    def guardar_cliente():
        if not e_nombre.get().strip():
            return messagebox.showerror("Error","Nombre obligatorio")
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("""INSERT INTO clientes (nombre,apellido,telefono,email,direccion,ciudad,codigo_postal,fecha_registro)
                     VALUES (?,?,?,?,?,?,?,?)""",
                  (e_nombre.get().strip(), e_apellido.get().strip(), e_tel.get().strip(),
                   e_email.get().strip(), e_dir.get().strip(), e_ciudad.get().strip(),
                   e_cp.get().strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit(); conn.close()
        cargar_listado()

    ttk.Button(form, text="Guardar Cliente", command=guardar_cliente).grid(row=4, column=0, pady=6)

    cols = ("cliente_id","nombre","apellido","telefono","email","direccion","ciudad","cp")
    tree_clientes = ttk.Treeview(frame, columns=cols, show="headings")
    for c in cols: tree_clientes.heading(c, text=c.capitalize())
    tree_clientes.pack(fill="both", expand=True, padx=10, pady=5)

    def cargar_listado():
        for r in tree_clientes.get_children(): tree_clientes.delete(r)
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("SELECT cliente_id,nombre,apellido,telefono,email,direccion,ciudad,codigo_postal FROM clientes ORDER BY nombre")
        for row in c.fetchall(): tree_clientes.insert("", tk.END, values=row)
        conn.close()

    def editar_cliente(_evt=None):
        sel = tree_clientes.selection()
        if not sel: return
        vals = tree_clientes.item(sel[0])["values"]
        cliente_id = vals[0]
        win = tk.Toplevel(frame); win.title("Editar Cliente")
        labels = ["Nombre","Apellido","Teléfono","Email","Dirección","Ciudad","CP"]
        entries = {}
        for i,(lbl,val) in enumerate(zip(labels, vals[1:])):
            tk.Label(win,text=lbl).grid(row=i,column=0)
            e=tk.Entry(win,width=40); e.insert(0,val); e.grid(row=i,column=1); entries[lbl.lower()]=e
        def guardar():
            conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("""UPDATE clientes SET nombre=?,apellido=?,telefono=?,email=?,direccion=?,ciudad=?,codigo_postal=? WHERE cliente_id=?""",
                      (entries["nombre"].get(),entries["apellido"].get(),entries["teléfono"].get(),
                       entries["email"].get(),entries["dirección"].get(),entries["ciudad"].get(),
                       entries["cp"].get(),cliente_id))
            conn.commit();conn.close();cargar_listado();win.destroy()
        tk.Button(win,text="Guardar",command=guardar).grid(row=len(labels),column=0,columnspan=2,pady=10)

    tree_clientes.bind("<Double-1>", editar_cliente)
    cargar_listado()

def refrescar_clientes():
    try:
        for r in tree_clientes.get_children(): tree_clientes.delete(r)
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("SELECT cliente_id,nombre,apellido,telefono,email,direccion,ciudad,codigo_postal FROM clientes ORDER BY nombre")
        for row in c.fetchall(): tree_clientes.insert("", tk.END, values=row)
        conn.close()
    except Exception as e:
        print("Error refrescando clientes:", e)
