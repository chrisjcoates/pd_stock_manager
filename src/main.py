from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from database.database import Database


def run_app():
    """Runs the application"""

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


def try_connect_to_db():
    """Attempt to connect to the main database, if connection fails ask the user if
    they want to run the application without connecting to the main database."""

    # check the database connection
    database = Database().check_db_connection()
    # if connection is found run application
    if database == True:
        run_app()
    else:
        print("Failed to connect to database.")
        # ask dev if they want to run app without main database
        run_debug_mode = input(
            "Would you like to run the app in without the main database connection? (y/n): "
        )
        # run app if dev inputs y
        if run_debug_mode.lower() == "y":
            run_app()


if __name__ == "__main__":
    try_connect_to_db()
