from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QTableWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QTableWidgetItem,
    QMessageBox,
)
from database.database import Database
from PySide6.QtCore import Qt, Signal, QDate
from datetime import datetime
from psycopg2 import errors
from classes.functions import get_style_path


class Edit_Location(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.setStyleSheet(get_style_path())

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Edit Location")
        self.setWindowModality(Qt.ApplicationModal)

        # Current records items
        self.items = []

        # Separate array for new items
        self.additional_items = []

        # Removed items
        self.removed_items = []

        self.record_id = record_id

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()

        self.get_location(self.record_id)
        self.get_order_items(self.record_id)

        self.resize(760, 600)

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

        headers = ["Bay Name", "Description", "Location ID", "Bay ID"]

        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 450)
        self.table.hideColumn(2)
        self.table.hideColumn(3)

        layout.addWidget(self.table)

        self.window_layout.addWidget(widget)

    def save_btn_widget(self):

        widget = QWidget()
        layout = QHBoxLayout(widget)

        save_btn = QPushButton("Save & Exit")
        save_btn.clicked.connect(self.save_order_btn_click)

        layout.addWidget(save_btn)

        self.window_layout.addWidget(widget)

    def get_location(self, id):

        sql_query = """
                    SELECT 
                        locationName, 
                        locations.locationDescription, 
                        locations.locationAddress, 
                        locations.locationCity, 
                        locations.locationPostCode
                    FROM locations
                    WHERE locationID = %(id)s;
                    """

        arg = {"id": self.record_id}

        data = Database().custom_query(sql_query, arg)

        self.location_name.setText(str(data[0][0]))
        self.description.setText(str(data[0][1]))
        self.address.setText(data[0][2])
        self.city.setText(data[0][3])
        self.post_code.setText(data[0][4])

    def get_order_items(self, order_id):

        sql_query = """
                    SELECT 
                        bays.bayName,
                        bays.bayDescription,
                        bays.locationID,
                        bays.bayID
                    FROM bays
                    WHERE bays.locationID = %(id)s
                    ORDER BY bays.bayID;
                    """

        arg = {"id": order_id}

        data = Database().custom_query(sql_query, arg)

        for row in data:
            self.items.append(row)

        self.table.setRowCount(len(self.items))

        for row_index, row_data in enumerate(self.items):
            for col_index, cell_data in enumerate(row_data):
                self.table.setItem(
                    row_index, col_index, QTableWidgetItem(str(cell_data))
                )

    def add_item(self):

        bay_input = self.bay.text()
        bay_desc_input = self.bay_description.text()

        if bay_input:
            new_item = (bay_input, bay_desc_input)
            self.additional_items.append(new_item)

            self.table.insertRow(self.table.rowCount())

        for column, data in enumerate(new_item):
            item = QTableWidgetItem(str(data))
            self.table.setItem(self.table.rowCount() - 1, column, item)

        self.bay.clear()
        self.bay_description.clear()

    def save_order_btn_click(self):

        self.save_order()

        self.close()

    def save_order(self):

        self.location_name.setFocus()

        ###########################################
        # Insert Additional Items into bays table #
        ###########################################

        insert_sql = """
                        INSERT INTO bays (bayName, bayDescription, locationID)
                        VALUES (%s, %s, %s);
                     """

        if len(self.additional_items) > 0:
            try:
                database = Database()
                database.connect_to_db()

                for row in self.additional_items:
                    row_item = [row[0], row[1]]
                    if len(row) == 3:
                        row_item.append(row[2])
                    else:
                        row_item.append(self.record_id)

                    database.cursor.execute(insert_sql, tuple(row_item))
                database.conn.commit()
            except Exception as e:
                database.conn.rollback()
                print(f"save_order(): <INSERT ADDITIONAL ITEMS> {e}")
            finally:
                database.disconnect_from_db()

        ########################################
        # Delete removed items from bays table #
        ########################################

        delete_sql = """
                        DELETE FROM bays
                        WHERE bayID = %s;
                     """

        if len(self.removed_items) > 0:
            try:
                database = Database()
                database.connect_to_db()

                for row in self.removed_items:
                    database.cursor.execute(delete_sql, (row[3],))
                database.conn.commit()
            except errors.ForeignKeyViolation as e:
                database.conn.rollback()

                msg = QMessageBox(self)
                msg.setText(
                    f"Deletion failed, there is stock set to this bay, please change the bay for that stock item first."
                )
                msg.setWindowTitle("Warning")
                response = msg.exec()
            except Exception as e:
                database.conn.rollback()
                print(f"save_order(): <DELETE REMOVED ITEMS> {e}")
            finally:
                database.disconnect_from_db()

        ###########################################
        # Update location details from bays table #
        ###########################################

        update_sql = """
                        UPDATE locations
                            SET locationName = %s,
                                locationDescription = %s,
                                locationAddress = %s,
                                locationCity = %s,
                                locationPostCode = %s
                        WHERE locationID = %s;
                    """

        try:
            location = (
                self.location_name.text(),
                self.description.text(),
                self.address.text(),
                self.city.text(),
                self.post_code.text(),
                self.record_id,
            )

            database = Database()
            database.connect_to_db()

            database.cursor.execute(update_sql, location)
            database.conn.commit()
        except Exception as e:
            database.conn.rollback()
            print(f"save_order(): <Update location details> {e}")
        finally:
            database.disconnect_from_db()

        #########################################
        # Update existing items from bays table #
        #########################################

        current_items = []

        try:
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")

                current_items.append(tuple(row_data))
        except Exception as e:
            print(f"save_order() 'looping through current_items': {e}")

        update_sql = """
                        UPDATE bays
                        SET bayName = %s,
                            bayDescription = %s
                        WHERE bayID = %s;
                    """

        if len(current_items) > 0:
            try:
                database = Database()
                database.connect_to_db()

                for row in current_items:
                    database.cursor.execute(
                        "SELECT COUNT(*) FROM bays WHERE bayID = %s", (row[3],)
                    )
                    if database.cursor.fetchone()[0] > 0:
                        database.cursor.execute(
                            update_sql,
                            (
                                row[0],
                                row[1],
                                row[3],
                            ),
                        )
                    database.conn.commit()
            except Exception as e:
                database.conn.rollback()
                print(f"save_order(): <UPDATE EXISITING ITEMS> {e}")
                msg = QMessageBox(self)
                msg.setText(f"Error updating location, {e}")
                msg.setWindowTitle("Message")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            finally:
                database.disconnect_from_db()
                # Create message box to tell used record was saved
                msg = QMessageBox(self)
                msg.setText("Location record has been updated.")
                msg.setWindowTitle("Message")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()

    def remove_item(self):

        selected_row = self.table.currentRow()

        if selected_row < len(self.items):
            try:
                removed_row = self.items.pop(selected_row)
                self.removed_items.append(removed_row)
                self.table.removeRow(selected_row)
            except Exception as e:
                print(f"No items to remove: {e}")
        else:
            # Work out index for additional items list
            index = selected_row - len(self.items)

            try:
                removed_row = self.additional_items.pop(index)
                self.removed_items.append(removed_row)
                self.table.removeRow(selected_row)
            except Exception as e:
                print(f"No items to remove: {e}")
