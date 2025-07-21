from tkinter import *
import subprocess

ventana = Tk()
ventana.title("Sistema de Reparaciones")

Label(ventana, text="Selecciona una opción:").pack(pady=10)

Button(ventana, text="Registrar Reparación", width=30, command=lambda: subprocess.Popen(["python", "registro_ticket.py"])).pack(pady=5)
Button(ventana, text="Ver Inventario", width=30, command=lambda: subprocess.Popen(["python", "inventario.py"])).pack(pady=5)

ventana.mainloop()
