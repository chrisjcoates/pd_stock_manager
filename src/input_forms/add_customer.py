from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from database.database import Database
from classes.functions import get_style_path


class AddCustomer(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add New Customer")

        self.setStyleSheet(get_style_path())

        self.top_layout = QVBoxLayout(self)
        main_layout_widget = QWidget()
        self.main_layout = QHBoxLayout(main_layout_widget)
        self.page_layout = QFormLayout()
        self.page_widget = QWidget()
        self.page_widget.setLayout(self.page_layout)
        self.setWindowModality(Qt.ApplicationModal)

        self.create_widgets()

        self.main_layout.addWidget(self.page_widget)
        self.top_layout.addWidget(main_layout_widget)

        self.product_picture()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def create_widgets(self):
        """Create the widgets for the input form"""
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter customer name")
        self.name_input.setFixedWidth(175)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setFixedWidth(175)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.email_input.setFixedWidth(175)

        # Create submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.create_product)

        # Add widgets the the grid layout
        self.page_layout.addRow("Customer Name: ", self.name_input)
        self.page_layout.addRow("Phone: ", self.phone_input)
        self.page_layout.addRow("Email: ", self.email_input)
        self.page_layout.addRow(submit_button)

    def product_picture(self):
        picture_widget = QLabel(text="Image Placeholder")
        picture_widget.setAlignment(Qt.AlignCenter)
        picture_widget.setStyleSheet("background-color: white;")
        picture_widget.setMinimumWidth(300)
        self.main_layout.addWidget(picture_widget)

    def create_product(self):
        """
        Create a product and insert the data into the database,
        Creates a record in the product table, and the stock table.
        """
        # Get the values from the input forms controls
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()

        try:
            # Insert the records into the database
            Database().insert_new_customer(
                name=name,
                phone=phone,
                email=email,
            )

            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("Customer record has been created.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except Exception as e:
            print(e)
            msg = QMessageBox(self)
            msg.setText(f"Error creating customer record, {e}")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        # destroy the form object(close)
        self.close()
