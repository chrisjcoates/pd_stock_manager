from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal


class DeletePopup(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.record_id = record_id

        self.setWindowTitle("Delete Product")
        self.setFixedSize(500, 150)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.add_widgets()

        self.setFixedSize(self.size())

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def add_widgets(self):
        # Set delete confirmation text
        message = "Are you sure you want to delete the product from the database?"
        # Create label
        label = QLabel(message)
        self.main_layout.addWidget(label)

        # Create button layout
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)

        # Create buttons
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")

        # Add buttons to layout
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)

        # Add button widget to main layout
        self.main_layout.addWidget(btn_widget)

    def yes_btn_click(self):
        pass

    def no_btn_click(self):
        pass


app = QApplication([])
window = DeletePopup()
window.show()
app.exec()
