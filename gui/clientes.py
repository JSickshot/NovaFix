import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import DB

tree_clientes = None

def styled_entry(parent, width=20):
    return tk.Entry(parent, width=width, font=("Segoe UI", 11),
                    bg="#222222", fg="white", insertbackground="white", relief="flat")

def styled_label(parent, text):
    return tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                    bg="black", fg="#DAA621")

def cargar_tab_clientes(frame):
    global tree_clientes

    form = ttk.LabelFrame(frame, text="Alta Cliente", style="Custom.TLabelframe")
    form.pack(fill="x", padx=10, pady=10)

    e_nombre = styled_entry(form, 24)
    e_apellido = styled_entry(form, 24)
    e_tel = styled_entry(form, 20)
    e_email = styled_entry(form, 28)
    e_dir = styled_entry(form, 48)
    e_ciudad = styled_entry(form, 24)
    e_cp = styled_entry(form, 10)

    styled_label(form, "Nombre:").grid(row=0, column=0, sticky="w"); e_nombre.grid(row=0, column=1)
    styled_label(form, "Apellido:").grid(row=0, column=2, sticky="w"); e_apellido.grid(row=0, column=3)
    styled_label(form, "Teléfono:").grid(row=1, column=0, sticky="w"); e_tel.grid(row=1, column=1)
    styled_label(form, "Email:").grid(row=1, column=2, sticky="w"); e_email.grid(row=1, column=3)
    styled_label(form, "Dirección:").grid(row=2, column=0, sticky="w"); e_dir.grid(row=2, column=1, columnspan=3, sticky="we")
    styled_label(form, "Ciudad:").grid(row=3, column=0, sticky="w"); e_ciudad.grid(row=3, column=1)
    styled_label(form, "CP:").grid(row=3, column=2, sticky="w"); e_cp.grid(row=3, column=3)

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

    ttk.Button(form, text="Guardar Cliente", style="Custom.TButton", command=guardar_cliente).grid(row=4, column=0, pady=6)

    # --- Treeview ---
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
