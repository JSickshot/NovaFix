from database import init_db, verificar_esquema
import tkinter as tk
from gui.login import LoginWindow

if __name__ == "__main__":
    init_db()
    verificar_esquema() 

    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
