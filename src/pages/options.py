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
from classes.functions import read_settings_json, write_settings_json


class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set the layout of the options screen
        self.page_layout = QVBoxLayout(self)

        # Add database details to screen
        self.database_details()

        # Add stretch to the layout
        # after adding widgets to layout to anchor them to the top of the screen
        self.page_layout.addStretch()

    def database_details(self):
        """Creates a widget to store and edit the database connection details"""

        # Create the main widget
        grid_widget = QWidget()
        grid_widget.setFixedSize(300, 250)
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
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.db_name_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        # Create save button
        db_save_btn = QPushButton(text="Save")
        # Add controls to the layout
        grid_layout.addWidget(host_label, 0, 0)
        grid_layout.addWidget(self.host_input, 0, 1)
        grid_layout.addWidget(port_label, 1, 0)
        grid_layout.addWidget(self.port_input, 1, 1)
        grid_layout.addWidget(db_name_label, 2, 0)
        grid_layout.addWidget(self.db_name_input, 2, 1)
        grid_layout.addWidget(user_label, 3, 0)
        grid_layout.addWidget(self.user_input, 3, 1)
        grid_layout.addWidget(pass_label, 4, 0)
        grid_layout.addWidget(self.pass_input, 4, 1)
        grid_layout.addWidget(db_save_btn, 5, 1)
        # bind function to button press
        db_save_btn.clicked.connect(self.update_db_settings)
        # set text from file
        self.read_database_settings()
        # Add grid widget to main class widget
        self.page_layout.addWidget(title_label)
        self.page_layout.addWidget(grid_widget)

    def read_database_settings(self):
        # Read the json file
        data = read_settings_json("src/settings/settings.json")

        # Set the database connection settings to the input fields
        self.host_input.setText(data["database"]["host"])
        self.port_input.setText(data["database"]["port"])
        self.db_name_input.setText(data["database"]["db_name"])
        self.user_input.setText(data["database"]["user"])
        self.pass_input.setText(data["database"]["password"])

    def update_db_settings(self):
        """Writes updated settings to the jason file"""
        # Get the input text values
        host = self.host_input.text()
        port = self.port_input.text()
        db_name = self.db_name_input.text()
        user = self.user_input.text()
        password = self.pass_input.text()
        # Write values to the json file
        write_settings_json(
            "src/settings/settings.json", host, port, db_name, user, password
        )
