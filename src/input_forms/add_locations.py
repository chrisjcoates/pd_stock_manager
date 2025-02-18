from PySide6.QtWidgets import (
    QCheckBox,
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QTableWidgetItem,
    QMessageBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QDate, Signal
from database.database import Database


class Add_Location_Window(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Create a new location")
        self.setWindowModality(Qt.ApplicationModal)

        self.items = []

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def order_details_widget(self):

        # Main widget layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # input widget layout
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.setLabelAlignment(Qt.AlignLeft)

        # button widget layout
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setAlignment(Qt.AlignBottom)

        # control widgets
        self.location_name = QLineEdit()
        self.location_name.setFixedWidth(175)
        self.location_name.setPlaceholderText("Enter location name")

        self.description = QLineEdit()
        self.description.setFixedWidth(350)
        self.description.setPlaceholderText("Enter description")

        self.address = QLineEdit()
        self.address.setFixedWidth(350)
        self.address.setPlaceholderText("Enter address")

        self.city = QLineEdit()
        self.city.setPlaceholderText("Enter city")

        self.post_code = QLineEdit()
        self.post_code.setPlaceholderText("Enter post code")

        self.bay = QLineEdit()
        self.bay.setPlaceholderText("Enter bay")

        self.bay_description = QLineEdit()
        self.bay_description.setPlaceholderText("Enter bay description")
        self.bay_description.setFixedWidth(350)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_item)

        # Add widgets to layout
        layout.addRow("Name: ", self.location_name)
        layout.addRow("Description:", self.description)
        layout.addRow("Address:", self.address)
        layout.addRow("City:", self.city)
        layout.addRow("Post Code:", self.post_code)
        layout.addRow("", QLabel())
        layout.addRow("Bay: ", self.bay)
        layout.addRow("Bay description: ", self.bay_description)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)

        main_layout.addWidget(widget)
        main_layout.addWidget(btn_widget)

        # Add main widget to main window
        self.window_layout.addWidget(main_widget)

    def item_table_widget(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.table = QTableWidget()

        headers = ["Bay Name", "Description"]

        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 450)

        layout.addWidget(self.table)

        self.window_layout.addWidget(widget)

    def save_btn_widget(self):

        widget = QWidget()
        layout = QHBoxLayout(widget)

        save_btn = QPushButton("Save & Exit")
        save_btn.clicked.connect(self.save_order_btn_click)

        layout.addWidget(save_btn)

        self.window_layout.addWidget(widget)

    def add_item(self):

        bay_input = self.bay.text()
        bay_desc_input = self.bay_description.text()

        if bay_input:
            new_item = (bay_input, bay_desc_input)
            self.items.append(new_item)

            self.table.insertRow(self.table.rowCount())

        for column, data in enumerate(new_item):
            item = QTableWidgetItem(str(data))
            self.table.setItem(self.table.rowCount() - 1, column, item)

    def save_order_btn_click(self):

        if self.location_name.text():
            self.save_order()
        else:
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText(
                "You need to enter a loaction name to be able to create an location."
            )
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        self.close()

    def save_order(self):

        location_name = self.location_name.text()
        description = self.description.text()
        address = self.address.text()
        city = self.city.text()
        post_code = self.post_code.text()

        # create dict for order table record
        order_dict = {
            "name": location_name,
            "description": description,
            "address": address,
            "city": city,
            "post_code": post_code,
        }

        # Insert into locations table
        sql_query = """
                    INSERT INTO locations (locationName, locationDescription, locationAddress, locationCity, locationPostCode)
                    VALUES (%(name)s, %(description)s, %(address)s, %(city)s, %(post_code)s)
                    RETURNING locationID;
                    """

        # Create database object and connect to db
        database = Database()
        database.connect_to_db()

        try:
            # Execute query
            database.cursor.execute(sql_query, order_dict)
            # get location id
            location_id = database.cursor.fetchone()
            location_id = location_id[0]

            # Insert into order item table
            sql_query = """
                        INSERT INTO bays (bayName, bayDescription, locationID)
                        VALUES (%(bay_name)s, %(bay_description)s, %(location_id)s);
                        """

            if len(self.items) > 0:
                for row in self.items:
                    bay_name = row[0]
                    bay_description = row[1]
                    database.cursor.execute(
                        sql_query,
                        {
                            "bay_name": bay_name,
                            "bay_description": bay_description,
                            "location_id": location_id,
                        },
                    )

        except Exception as e:
            print(f"Error inserting data {e}")

        try:
            database.conn.commit()
        except Exception as e:
            print(e)

        database.disconnect_from_db()

    def remove_item(self):

        selected_row = self.table.currentRow()

        try:
            self.items.pop(selected_row)
            self.table.removeRow(selected_row)
        except:
            print("No items to remove.")
