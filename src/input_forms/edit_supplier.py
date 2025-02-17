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
)
from PySide6.QtCore import Qt, Signal
from database.database import Database


class EditSupplier(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.setWindowTitle("Edit Supplier")

        self.record_id = record_id
        self.main_layout = QHBoxLayout(self)
        self.page_layout = QFormLayout()
        self.page_widget = QWidget()
        self.page_widget.setLayout(self.page_layout)
        self.setWindowModality(Qt.ApplicationModal)

        self.create_widgets()
        self.get_selected_record()

        self.main_layout.addWidget(self.page_widget)

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def create_widgets(self):
        """Create the widgets for the input form"""
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(175)
        self.contact_fn = QLineEdit()
        self.contact_fn.setPlaceholderText("Enter first name")
        self.contact_fn.setFixedWidth(175)
        self.contact_ln = QLineEdit()
        self.contact_ln.setFixedWidth(175)
        self.contact_ln.setPlaceholderText("Enter last name")
        self.phone = QLineEdit()
        self.phone.setFixedWidth(175)
        self.email = QLineEdit()
        self.email.setFixedWidth(175)

        # Create submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.update_supplier)

        # Add widgets the the grid layout
        self.page_layout.addRow("Customer Name: ", self.name_input)
        self.page_layout.addRow("Contact First Name: ", self.contact_fn)
        self.page_layout.addRow("Contact Last Name: ", self.contact_ln)
        self.page_layout.addRow("Phone: ", self.phone)
        self.page_layout.addRow("Email: ", self.email)
        self.page_layout.addRow(submit_button)


    def get_selected_record(self):

        database = Database()
        database.connect_to_db()

        get_customer_sql = """SELECT supplierName, contactFirstName, contactLastName, supplierPhone, supplierEmail FROM supplier WHERE supplierID = %s;"""

        try:
            database.cursor.execute(get_customer_sql, (self.record_id,))
            selected_record = database.cursor.fetchone()
            database.conn.commit()
        except Exception as e:
            database.conn.rollback()
            print(f"get_selected_record(): {e}")
        finally:
            database.disconnect_from_db()

        self.name_input.setText(selected_record[0])
        self.contact_fn.setText(selected_record[1])
        self.contact_ln.setText(selected_record[2])
        self.phone.setText(selected_record[3])
        self.email.setText(selected_record[4])

    def update_supplier(self):
        """
        Update a supplier and insert the data into the database,
        Updates a record in the supplier table, and the stock table.
        """
        # Get the values from the input forms controls
        name = self.name_input.text()
        first_name = self.contact_fn.text()
        last_name = self.contact_ln.text()
        phone = self.phone.text()
        email = self.email.text()

        database = Database()
        database.connect_to_db()

        update_customer_sql = """
                                UPDATE supplier
                                SET supplierName = %s,
                                    contactFirstName = %s,
                                    contactLastName = %s,
                                    supplierPhone = %s,
                                    supplierEmail = %s
                                WHERE supplierID = %s;"""

        try:
            database.cursor.execute(
                update_customer_sql, (name, first_name, last_name,  phone, email, self.record_id)
            )
            database.conn.commit()
        except Exception as e:
            database.conn.rollback()
            print(f"update_supplier(): {e}")
            print(e)
            msg = QMessageBox(self)
            msg.setText(f"Error updating supplier record, {e}")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        finally:
            database.disconnect_from_db()
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("Supplier record has been updated.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        # destroy the form object(close)
        self.close()
