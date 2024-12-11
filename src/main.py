from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from database.database import Database

def run_app():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

def try_connect_to_db():
    database = Database().connect_to_db()
    if database == True:
        run_app()
    else:
        print("Failed to connect to database.")
        run_debug_mode = input("would you like to run the app in with out database connection? (y/n): ")
        if run_debug_mode.lower() == 'y':
            run_app()
            

if __name__ == '__main__':
    try_connect_to_db()