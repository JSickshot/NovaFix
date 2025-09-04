import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
DB = "novafix_pos.db"

def cargar_tab_inventario(frame):
    # Formulario
    form_frame = ttk.LabelFrame(frame, text="Agregar / Editar Pieza")
    form_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(form_frame, text="Pieza:").grid(row=0, column=0, sticky='w')
    entry_pieza = tk.Entry(form_frame, width=30)
    entry_pieza.grid(row=0, column=1, sticky='w')

    tk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky='w')
    entry_descripcion = tk.Entry(form_frame, width=50)
    entry_descripcion.grid(row=1, column=1, sticky='w')

    tk.Label(form_frame, text="Stock:").grid(row=2, column=0, sticky='w')
    entry_stock = tk.Entry(form_frame, width=10)
    entry_stock.grid(row=2, column=1, sticky='w')

    def guardar_pieza():
        pieza = entry_pieza.get().strip()
        descripcion = entry_descripcion.get().strip()
        stock = entry_stock.get().strip()
        if not pieza or not stock:
            messagebox.showerror("Error", "Debe llenar Pieza y Stock.")
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
        cargar_inventario_tree()

    tk.Button(form_frame, text="Guardar Pieza", command=guardar_pieza).grid(row=3, column=0, pady=10)

    # Treeview
    tree_inventario = ttk.Treeview(frame, columns=("pieza", "descripcion", "stock"), show='headings')
    tree_inventario.heading("pieza", text="Pieza")
    tree_inventario.heading("descripcion", text="Descripción")
    tree_inventario.heading("stock", text="Stock")
    tree_inventario.pack(fill='both', expand=True, padx=10, pady=5)

    def cargar_inventario_tree():
        for row in tree_inventario.get_children():
            tree_inventario.delete(row)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT pieza, descripcion, stock FROM inventario ORDER BY pieza")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            tree_inventario.insert("", tk.END, values=row)

    cargar_inventario_tree()
