import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB

tree_inv = None

def styled_entry(parent, width=20):
    return tk.Entry(parent, width=width, font=("Segoe UI", 11),
                    bg="#222222", fg="white", insertbackground="white", relief="flat")

def styled_label(parent, text):
    return tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                    bg="black", fg="#DAA621")

def cargar_tab_inventario(frame):
    global tree_inv

    form = ttk.LabelFrame(frame, text="Alta Inventario", style="Custom.TLabelframe")
    form.pack(fill="x", padx=10, pady=10)

    e_pieza = styled_entry(form, 24)
    e_desc = styled_entry(form, 48)
    e_stock = styled_entry(form, 10)
    e_precio = styled_entry(form, 10)

    styled_label(form, "Pieza:").grid(row=0, column=0); e_pieza.grid(row=0, column=1)
    styled_label(form, "Descripción:").grid(row=1, column=0); e_desc.grid(row=1, column=1, columnspan=3)
    styled_label(form, "Stock:").grid(row=2, column=0); e_stock.grid(row=2, column=1)
    styled_label(form, "Precio:").grid(row=2, column=2); e_precio.grid(row=2, column=3)

    def guardar():
        try:
            stock = int(e_stock.get()); precio = float(e_precio.get())
        except: return messagebox.showerror("Error","Stock=entero, Precio=decimal")
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("INSERT OR REPLACE INTO inventario (pieza,descripcion,stock,precio_unitario) VALUES (?,?,?,?)",
                  (e_pieza.get().strip(), e_desc.get().strip(), stock, precio))
        conn.commit();conn.close();cargar_listado()

    ttk.Button(form,text="Guardar Pieza",style="Custom.TButton",command=guardar).grid(row=3,column=0,pady=6)

    cols=("pieza_id","pieza","descripcion","stock","precio_unitario")
    tree_inv=ttk.Treeview(frame,columns=cols,show="headings")
    for c in cols: tree_inv.heading(c,text=c.capitalize())
    tree_inv.pack(fill="both",expand=True,padx=10,pady=5)

    def cargar_listado():
        for r in tree_inv.get_children(): tree_inv.delete(r)
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("SELECT pieza_id,pieza,descripcion,stock,precio_unitario FROM inventario ORDER BY pieza")
        for row in c.fetchall(): tree_inv.insert("",tk.END,values=row)
        conn.close()

    cargar_listado()

def refrescar_inventario():
    try:
        for r in tree_inv.get_children(): tree_inv.delete(r)
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("SELECT pieza_id,pieza,descripcion,stock,precio_unitario FROM inventario ORDER BY pieza")
        for row in c.fetchall(): tree_inv.insert("",tk.END,values=row)
        conn.close()
    except Exception as e:
        print("Error refrescando inventario:", e)
