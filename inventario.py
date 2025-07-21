from tkinter import *
from utils import conectar_db, crear_tablas

crear_tablas()

def cargar_inventario():
    listbox.delete(0, END)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, descripcion, cantidad FROM inventario")
    for fila in cursor.fetchall():
        listbox.insert(END, f"{fila[0]} - {fila[1]}: {fila[2]} piezas")
    conn.close()

ventana = Tk()
ventana.title("Inventario disponible")

listbox = Listbox(ventana, width=50)
listbox.pack(padx=20, pady=20)

Button(ventana, text="Actualizar Inventario", command=cargar_inventario).pack()

cargar_inventario()
ventana.mainloop()
