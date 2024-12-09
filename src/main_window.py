from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QPushButton, QToolBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Management System")
        self.resize(800, 600)

