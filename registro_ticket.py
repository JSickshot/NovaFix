from tkinter import *
from tkinter import messagebox
from reportlab.pdfgen import canvas
import datetime
from utils import conectar_db, crear_tablas, TICKET_FOLDER

crear_tablas()

def guardar_ticket():
    nombre = e_nombre.get()
    telefono = e_telefono.get()
    correo = e_correo.get()
    producto = e_producto.get()
    error = e_error.get()

    if not nombre or not telefono or not producto or not error:
        messagebox.showerror("Faltan datos", "Todos los campos marcados con * son obligatorios.")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES (?, ?, ?)", (nombre, telefono, correo))
    cliente_id = cursor.lastrowid

    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO tickets (cliente_id, producto, error, fecha) VALUES (?, ?, ?, ?)",
                   (cliente_id, producto, error, fecha))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    archivo = f"{TICKET_FOLDER}/ticket_{ticket_id}.pdf"
    c = canvas.Canvas(archivo)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"TICKET DE RECEPCIÓN #{ticket_id}")
    c.drawString(100, 780, f"Cliente: {nombre}")
    c.drawString(100, 760, f"Producto: {producto}")
    c.drawString(100, 740, f"Error: {error}")
    c.drawString(100, 720, f"Fecha: {fecha}")
    c.save()

    messagebox.showinfo("Ticket guardado", f"Ticket #{ticket_id} guardado correctamente.")
    limpiar()

def limpiar():
    e_nombre.delete(0, END)
    e_telefono.delete(0, END)
    e_correo.delete(0, END)
    e_producto.delete(0, END)
    e_error.delete(0, END)

ventana = Tk()
ventana.title("Registro de Reparación")

Label(ventana, text="Nombre *").grid(row=0, column=0)
Label(ventana, text="Teléfono *").grid(row=1, column=0)
Label(ventana, text="Correo").grid(row=2, column=0)
Label(ventana, text="Producto *").grid(row=3, column=0)
Label(ventana, text="Error *").grid(row=4, column=0)

e_nombre = Entry(ventana, width=40)
e_telefono = Entry(ventana, width=40)
e_correo = Entry(ventana, width=40)
e_producto = Entry(ventana, width=40)
e_error = Entry(ventana, width=40)

e_nombre.grid(row=0, column=1)
e_telefono.grid(row=1, column=1)
e_correo.grid(row=2, column=1)
e_producto.grid(row=3, column=1)
e_error.grid(row=4, column=1)

Button(ventana, text="Guardar y generar ticket", command=guardar_ticket).grid(row=5, column=0, columnspan=2, pady=10)

ventana.mainloop()
