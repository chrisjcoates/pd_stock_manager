from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtCore import Qt
from database.database import Database
from classes.functions import export_array_to_excel
from input_forms.add_locations import Add_Location_Window
from input_forms.edit_location import Edit_Location
from psycopg2 import errors
from classes.functions import get_style_path


class LocationsTable(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_style_path())

        self.page_layout = QVBoxLayout(self)

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0
        # Set the database object
        self.data = None

        # Add widgets to layout
        self.create_button_widgets()
        self.create_text_filter_widget()
        self.create_table_widget()
        self.update_table_data()

    def update_table_data(self):

        select_sql = """
                    SELECT
                        locations.locationID,
                        locations.locationName,
                        locations.locationDescription,
                        locations.locationAddress,
                        locations.locationCity,
                        locations.locationPostCode,
                        count(bays.bayID) as num_bays
                    FROM
                        locations
                    LEFT JOIN bays ON bays.locationID = locations.locationID
                    GROUP BY locations.locationID
                    ORDER BY locationID;
                    """
        database = Database()
        try:
            database.connect_to_db()
            database.cursor.execute(select_sql)
            returned_data = database.cursor.fetchall()
            if returned_data:
                self.data = returned_data
        except Exception as e:
            print(f"update_table_data(): {e}")
        finally:
            database.disconnect_from_db()

        try:
            self.table_widget.setRowCount(len(self.data))
        except:
            self.table_widget.setRowCount(0)

        if self.data:
            for row_index, row_data in enumerate(self.data):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.table_widget.setItem(row_index, col_index, item)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def create_button_widgets(self):
        """Create button widgets"""
        # Create button widgets
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        # Create buttons
        add_button = QPushButton(text="Add Location")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")
        export_btn = QPushButton(text="Export data")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        # button_layout.addWidget(export_btn)

        # button binds
        add_button.clicked.connect(self.open_add_location_form)
        edit_button.clicked.connect(self.open_edit_location_form)
        delete_button.clicked.connect(self.delete_location)
        # export_btn.clicked.connect(self.export_to_excel)

        self.page_layout.addWidget(button_widget)

    def create_text_filter_widget(self):
        # Create filter widget
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # Create filter text box
        filter_line_edit = QLineEdit()
        filter_widget.setMaximumWidth(500)
        # Create filter / clear button
        filter_btn = QPushButton(text="Filter")
        clear_filter_btn = QPushButton(text="Clear")
        # add button click events
        filter_btn.clicked.connect(lambda: filter_data())
        clear_filter_btn.clicked.connect(lambda: clear_filter())
        # Add on enter event to text filter
        filter_line_edit.returnPressed.connect(
            lambda: (
                filter_data() if len(filter_line_edit.text()) > 0 else clear_filter()
            )
        )
        # Add the widgets rto the layout
        filter_layout.addWidget(filter_line_edit)
        filter_layout.addWidget(filter_btn)
        filter_layout.addWidget(clear_filter_btn)
        # Add to main class layout
        self.page_layout.addWidget(filter_widget)

        def filter_data():
            """Function to filter the data based on text input value"""
            # Get filter text
            filter_text = filter_line_edit.text()
            self.update_table_data()
            try:
                if filter_text:
                    # Loop through each row in data and keep only records that match the filter
                    filtered_data = [
                        row
                        for row in self.data
                        if any(filter_text.lower() in str(cell).lower() for cell in row)
                    ]
                    # Set the data to filtered data
                    self.data = filtered_data

                    # update row and column count, and refresh table
                    if len(self.data) > 0:
                        self.table_widget.clearContents()
                        self.table_widget.setRowCount(len(self.data))
                        for row_index, row_data in enumerate(self.data):
                            for col_index, col_data in enumerate(row_data):
                                self.table_widget.setItem(
                                    row_index,
                                    col_index,
                                    QTableWidgetItem(str(col_data)),
                                )
                        print("Data filtered.")
            except Exception as e:
                print(e)

        def clear_filter():
            """clears the current filter and returns the table data back to normal"""
            try:
                self.update_table_data()
                # Clear the filter text
                filter_line_edit.clear()
                print("Data un-filtered.")
            except Exception as e:
                print(e)

    def create_table_widget(self):
        """Creates a table widget"""
        header_labels = [
            "ID",
            "Name",
            "Description",
            "Address",
            "City",
            "Post Code",
            "No. Bays",
        ]
        self._column_count = len(header_labels)
        # Create table widget
        self.table_widget = QTableWidget(self)
        # remove the row header
        self.table_widget.verticalHeader().setVisible(False)
        # Set row highlighting to full row
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(self._row_count)
        self.table_widget.setColumnCount(self._column_count)
        # Set table column header labels
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        # Set the table column widths
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.setColumnWidth(2, 350)
        self.table_widget.setColumnWidth(3, 350)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 200)

    def open_add_location_form(self):

        def update_table():
            self.update_table_data()
            self.add_customer_form.destroy()

        """Opens the add product input form
        and adds close event signal to update the table data
        """
        # Creates the product input form
        self.add_customer_form = Add_Location_Window()
        # Create an on close signal event to refresh the table data
        self.add_customer_form.closed_signal.connect(update_table)
        # Open the input form
        self.add_customer_form.show()

    def open_edit_location_form(self):

        def update_table():
            self.update_table_data()
            self.add_customer_form.destroy()

        """Opens the edit product input form
        and adds close event signal to update the table data
        """
        try:
            # Get the id of the current selected record
            current_record = self.current_record_selected()
            # Creates the product input form
            self.add_customer_form = Edit_Location(current_record)
            # Create an on close signal event to refresh the table data
            self.add_customer_form.closed_signal.connect(update_table)
            # Open the input form
            self.add_customer_form.show()
        except Exception as e:
            print(e)

    def current_record_selected(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            record_id_item = self.table_widget.item(selected_row, 0)
        try:
            if record_id_item:
                return record_id_item.text()
        except Exception as e:
            print(e)

    def delete_location(self):

        current_record = self.current_record_selected()

        msg = QMessageBox(self)
        msg.setText(
            f"This will delete the location record, are you sure you want to continue?"
        )
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = msg.exec()

        if response == QMessageBox.Yes:
            msg = QMessageBox(self)
            msg.setText(
                f"Location is about to be deleted, are you sure you want to continue?"
            )
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            response = msg.exec()
            if response == QMessageBox.Yes:

                database = Database()
                database.connect_to_db()

                delete_sql = """DELETE FROM locations
                                WHERE locationID = %s;"""

                try:
                    database.cursor.execute(
                        delete_sql, (self.current_record_selected(),)
                    )
                    database.conn.commit()
                except errors.ForeignKeyViolation as e:
                    database.conn.rollback()

                    msg = QMessageBox(self)
                    msg.setText(
                        f"Deletion failed, you need to remove the bay's for this location first."
                    )
                    msg.setWindowTitle("Warning")
                    response = msg.exec()
                except Exception as e:
                    database.conn.rollback()
                    print(f"delete_location(): {e}")
                finally:
                    database.disconnect_from_db()

        self.update_table_data()
