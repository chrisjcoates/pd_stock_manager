from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
import json


class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QVBoxLayout(self)

        grid_widget = QWidget()
        grid_widget.setMaximumWidth(400)
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)

        host_label = QLabel(text="Host")
        host_input = QLineEdit()

        port_label = QLabel(text="Port")
        port_input = QLineEdit()

        db_name_label = QLabel(text="Database Name")
        db_name_input = QLineEdit()

        user_label = QLabel(text="User Name")
        user_input = QLineEdit()

        pass_label = QLabel(text="Password")
        pass_input = QLineEdit()

        grid_layout.addWidget(host_label, 0, 0)
        grid_layout.addWidget(host_input, 0, 1)

        grid_layout.addWidget(port_label, 1, 0)
        grid_layout.addWidget(port_input, 1, 1)

        grid_layout.addWidget(db_name_label, 2, 0)
        grid_layout.addWidget(db_name_input, 2, 1)

        grid_layout.addWidget(user_label, 3, 0)
        grid_layout.addWidget(user_input, 3, 1)

        grid_layout.addWidget(pass_label, 4, 0)
        grid_layout.addWidget(pass_input, 4, 1)

        page_layout.addWidget(grid_widget)
