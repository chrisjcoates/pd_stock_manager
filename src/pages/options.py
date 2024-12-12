from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Qt
import json


class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set the layout of the options screen
        self.page_layout = QVBoxLayout(self)

        # Add database details to screen
        self.database_details()

        # Add strech to the layout
        # after adding widgets to layout to anchor them to the top of the screen
        self.page_layout.addStretch()

    def database_details(self):
        """Creates a widget to store and edit the database connection details"""

        # Create the main widget
        grid_widget = QWidget()
        grid_widget.setFixedSize(300, 250)
        # Create boarder around widget
        # grid_widget.setStyleSheet(
        #     """QWidget {
        #                     border: 2px groove grey;
        #         }
        #         QLabel {
        #                     border: none;

        #                 }
        #         QLineEdit {
        #                     border: none;
        #         }
        #         QPushButton {
        #                     border: none;
        #         }
        #                     """
        # )
        # Create the widgets layout
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)
        # Create labels
        title_label = QLabel(text="Database Details")
        host_label = QLabel(text="Host")
        port_label = QLabel(text="Port")
        db_name_label = QLabel(text="Database Name")
        user_label = QLabel(text="User Name")
        pass_label = QLabel(text="Password")
        # Create text inputs
        host_input = QLineEdit()
        port_input = QLineEdit()
        db_name_input = QLineEdit()
        user_input = QLineEdit()
        pass_input = QLineEdit()
        # Create save button
        db_save_btn = QPushButton(text="Save")
        # Add controls to the layout
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
        grid_layout.addWidget(db_save_btn, 5, 1)
        # Add grid widget to main class widget
        self.page_layout.addWidget(title_label)
        self.page_layout.addWidget(grid_widget)
