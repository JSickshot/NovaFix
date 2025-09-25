import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB

def cargar_tab_inventario(frame):
    global tree_inv, cargar_listado

    form = ttk.LabelFrame(frame, text="Alta Inventario")
    form.pack(fill="x", padx=10, pady=10)

    e_pieza = tk.Entry(form, width=24)
    e_desc = tk.Entry(form, width=48)
    e_stock = tk.Entry(form, width=10)
    e_precio = tk.Entry(form, width=10)

    tk.Label(form, text="Pieza:").grid(row=0, column=0); e_pieza.grid(row=0, column=1)
    tk.Label(form, text="Descripción:").grid(row=1, column=0); e_desc.grid(row=1, column=1, columnspan=3)
    tk.Label(form, text="Stock:").grid(row=2, column=0); e_stock.grid(row=2, column=1)
    tk.Label(form, text="Precio:").grid(row=2, column=2); e_precio.grid(row=2, column=3)

    def guardar():
        try:
            stock = int(e_stock.get()); precio = float(e_precio.get())
        except: return messagebox.showerror("Error","Stock=entero, Precio=decimal")
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("INSERT OR REPLACE INTO inventario (pieza,descripcion,stock,precio_unitario) VALUES (?,?,?,?)",
                  (e_pieza.get().strip(), e_desc.get().strip(), stock, precio))
        conn.commit();conn.close();cargar_listado()

    ttk.Button(form,text="Guardar Pieza",command=guardar).grid(row=3,column=0,pady=6)

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

    def editar_inv(_evt=None):
        sel=tree_inv.selection()
        if not sel:return
        vals=tree_inv.item(sel[0])["values"];pid=vals[0]
        win=tk.Toplevel(frame);win.title("Editar Inventario")
        labels=["Pieza","Descripción","Stock","Precio"]
        entries={}
        for i,(lbl,val) in enumerate(zip(labels,vals[1:])):
            tk.Label(win,text=lbl).grid(row=i,column=0)
            e=tk.Entry(win,width=40);e.insert(0,val);e.grid(row=i,column=1);entries[lbl.lower()]=e
        def guardar():
            conn=sqlite3.connect(DB);c=conn.cursor()
            c.execute("UPDATE inventario SET pieza=?,descripcion=?,stock=?,precio_unitario=? WHERE pieza_id=?",
                      (entries["pieza"].get(),entries["descripción"].get(),entries["stock"].get(),entries["precio"].get(),pid))
            conn.commit();conn.close();cargar_listado();win.destroy()
        tk.Button(win,text="Guardar",command=guardar).grid(row=4,column=0,columnspan=2,pady=10)

    tree_inv.bind("<Double-1>",editar_inv)
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
