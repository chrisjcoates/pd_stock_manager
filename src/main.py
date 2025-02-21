from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QTimer, QSize
from main_window import MainWindow
from database.database import Database


def run_app():
    """Runs the application"""

    app = QApplication([])

    app.setWindowIcon(QIcon("src/icon/Pendle Icon.ico"))

    # Load the splash screen only when app starts
    splash_image = QPixmap("src/logo/Pendle_Logo.png").scaled(
        QSize(400, 300), Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    splash = QSplashScreen(
        splash_image, Qt.WindowStaysOnTopHint | Qt.WindowFullscreenButtonHint
    )

    splash.showMessage(
        "Stock App Loading...", Qt.AlignBottom | Qt.AlignCenter, Qt.black
    )
    splash.show()
    splash.raise_()

    # Create and show the main window after a delay
    def show_main_window():

        database_connected = Database().check_db_connection()
        if database_connected:
            window = MainWindow()
            window.showMaximized()
            splash.finish(window)
        else:
            connection_message = QMessageBox()
            connection_message.setText(
                """A connection to the database could not be established. Please check network connection. Contact Admin for help."""
            )
            connection_message.windowTitle = "No Connecton"
            connection_message.setStandardButtons(QMessageBox.Ok)
            connection_message.exec()

    QTimer.singleShot(3000, show_main_window)

    app.exec()


if __name__ == "__main__":
    run_app()
