from database import crear_tablas
from gui.login import LoginWindow
from gui.main_window import MainWindow

def run_app():
    def on_login_success(username, rol):
        
        app = MainWindow(username, rol)
        app.mainloop()

    
    login = LoginWindow(on_login_success)
    login.mainloop()

if __name__ == "__main__":
    crear_tablas()
    app = LoginWindow()
    app.mainloop()