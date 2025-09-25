from database import crear_tablas
from gui.login import LoginWindow

if __name__ == "__main__":
    crear_tablas()
    app = LoginWindow()
    app.mainloop()
