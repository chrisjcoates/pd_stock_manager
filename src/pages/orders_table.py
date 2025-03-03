from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QMessageBox,
    QFileDialog,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from database.database import Database
from popup_boxes.delete_product import DeletePopup
from classes.functions import export_array_to_excel
from classes.generate_picking_list import create_picking_list
from input_forms.add_order_items import Add_Items_Window
from input_forms.edit_order_items import Edit_Order_Items
import datetime
import os
from classes.functions import get_style_path


class OrdersTable(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_style_path())

        self.page_layout = QVBoxLayout(self)

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0
        # Set the database object
        self._database = Database()
        self.data = self._database.get_orders_data()
        self.update_row_column_count()

        # Add widgets to layout
        self.create_button_widgets()
        self.create_text_filter_widget()
        self.create_table_widget()

    def create_button_widgets(self):
        """Create button widgets"""
        # Create button widgets
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        # Create buttons
        add_button = QPushButton(text="Create Picking List")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")
        export_btn = QPushButton(text="Export data")
        pdf_btn = QPushButton(text="Create PDF")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        # button_layout.addWidget(export_btn)
        button_layout.addWidget(pdf_btn)

        # button binds
        add_button.clicked.connect(self.open_add_product_form)
        edit_button.clicked.connect(self.open_edit_product_form)
        delete_button.clicked.connect(self.delete_picking_list)
        # export_btn.clicked.connect(self.export_to_excel)
        pdf_btn.clicked.connect(self.create_pdf_report)

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
            self.data = self._database.get_orders_data()
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
                        self.update_row_column_count()
                        self.refresh_table(True)
                        print("Data filtered.")
            except Exception as e:
                print(e)

        def clear_filter():
            """clears the current filter and returns the table data back to normal"""
            try:
                # get data from database
                self.data = self._database.get_orders_data()
                # Update the row and column count
                self.update_row_column_count()
                # Refresh the table
                self.refresh_table()
                # Clear the filter text
                filter_line_edit.clear()
                print("Data un-filtered.")
            except Exception as e:
                print(e)

    def create_table_widget(self):
        """Creates a table widget"""
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
        self.table_widget.setHorizontalHeaderLabels(
            [
                "ID",
                "Sage No.",
                "Customer",
                "Delivery Date",
                "Picking Status",
                "Date Created",
                "Last Edit",
            ]
        )

        # Set the table column widths
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.setColumnWidth(2, 250)
        self.table_widget.setColumnWidth(3, 200)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 200)
        self.table_widget.setColumnWidth(6, 200)

        self.table_widget.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.Stretch
        )

    def refresh_table(self, filter=None):
        """refreshes the table data by querying the database to get the most upto data data"""
        # Update to db connection to current settings
        self._database.update_db_connection()
        if filter == None:
            # set data to the most recent data
            self.data = self._database.get_orders_data()
            print("Data retrieved")
            # update the row and column count
            if self.data:
                self.update_row_column_count()
        # Add data to table
        try:
            # Loop though data and add data to table
            for row_index, row_data in enumerate(self.data):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.table_widget.setItem(row_index, col_index, item)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        except Exception as e:
            print(e)

        self.format_qty_cells()

    def update_row_column_count(self):
        """updates the row and column count of the table widget"""
        no_data = False
        try:
            if self.data:
                # set row count to length of data
                self._row_count = len(self.data)
                # Set column count to 0
                self._column_count = 0
                # Loop through each row in data and increase column count
                for row in self.data:
                    for column in row:
                        self._column_count += 1
                    break

                # set the row and column count of the table widget
                try:
                    self.table_widget.setRowCount(self._row_count)
                    self.table_widget.setColumnCount(self._column_count)
                except:
                    pass
            else:
                no_data = True
        except Exception as e:
            print(e)

        if no_data:
            self._row_count = 0
            self._column_count = 7

    def open_add_product_form(self):

        def update_table():
            self.refresh_table()
            self.add_product_form.destroy()

        """Opens the add product input form
        and adds close event signal to update the table data
        """
        # Creates the product input form
        self.add_product_form = Add_Items_Window()
        # Create an on close signal event to refresh the table data
        self.add_product_form.closed_signal.connect(update_table)
        # Open the input form
        self.add_product_form.show()

    def open_edit_product_form(self):

        def update_table():
            self.refresh_table()
            self.add_product_form.destroy()

        """Opens the edit product input form
        and adds close event signal to update the table data
        """
        try:
            # Get the id of the current selected record
            current_record = self.current_record_selected()
            # Creates the product input form
            self.add_product_form = Edit_Order_Items(current_record)
            # Create an on close signal event to refresh the table data
            self.add_product_form.closed_signal.connect(update_table)
            # Open the input form
            self.add_product_form.show()
        except:
            pass

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

    def export_to_excel(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Select folder")

        export_array_to_excel(array=self.data, filepath=folder_path)

    def format_qty_cells(self):
        # Loop through each row in the table widget
        for row in range(self.table_widget.rowCount()):
            # set the qty / reorder fields as variables
            status_field = self.table_widget.item(row, 4)

            # check is the qty and reorder have values
            if status_field.text() == "WIP":
                status_field.setBackground(QColor(227, 182, 5))
            else:
                # Set cell colour to default
                status_field.setBackground(QColor(113, 191, 114))

    def delete_picking_list(self):

        current_record = self.current_record_selected()

        msg = QMessageBox(self)
        msg.setText(
            f"This will return all items back to stock and delete the picking list, are you sure you want to continue?"
        )
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = msg.exec()

        if response == QMessageBox.Yes:
            msg = QMessageBox(self)
            msg.setText(
                f"Data is about to be deleted, are you sure you want to continue?"
            )
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            response = msg.exec()
            if response == QMessageBox.Yes:

                database = Database()
                database.connect_to_db()

                select_sql = """SELECT stockID, orderItemQty, orderItemID
                                FROM order_item
                                WHERE orderID = %s;"""

                try:
                    database.cursor.execute(select_sql, (current_record,))
                    data = database.cursor.fetchall()

                    # Put items back into stock
                    if data:
                        for row in data:

                            update_sql = """UPDATE stock
                                            SET stockQty = stockQty + %s
                                            WHERE stockID IN (
                                                SELECT stockID
                                                FROM order_item
                                                WHERE stockID = %s AND removedFromStock = TRUE);"""

                            database.cursor.execute(update_sql, (row[1], row[0]))

                            # Delete order_items
                            delete_items_sql = (
                                """DELETE FROM order_item WHERE orderID = %s;"""
                            )

                            database.cursor.execute(delete_items_sql, (current_record,))

                    # Delete the picking list
                    delete_sql = """DELETE FROM orders
                                    WHERE orderID = %s;"""

                    database.cursor.execute(delete_sql, (current_record,))

                    database.conn.commit()
                except Exception as e:
                    print(f"delete_picking_list(): {e}")
                finally:
                    database.disconnect_from_db()

        self.refresh_table()

    def create_pdf_report(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Select folder")

        current_record = self.current_record_selected()

        if current_record:
            database = Database()
            database.connect_to_db()

            details_sql = """SELECT
                                customer.customerName, 
                                orders.sageNumber,
                                TO_CHAR(orders.deliveryDate, 'DD/MM/YYYY')
                            FROM orders
                            INNER JOIN customer ON customer.customerID = orders.customerID
                            WHERE orders.orderID = %s;"""

            line_items_sql = """SELECT
                                    CAST(ROW_NUMBER() OVER () AS TEXT) AS row_num,
                                    product.productName,
                                    product.productCode,
                                    SUM(order_item.orderItemQty) AS total_order_qty,
                                    locations.locationName,
                                    bays.bayName,
                                    '' AS picked
                                FROM order_item
                                INNER JOIN stock ON order_item.stockID = stock.stockID
                                INNER JOIN bays ON bays.bayID = stock.BayID
                                INNER JOIN locations ON locations.locationID = bays.locationID
                                INNER JOIN product ON product.productID = stock.ProductID
                                WHERE order_item.orderID = %s AND order_item.pickingStatus = 'WIP'
                                GROUP BY product.productID, product.productName, product.productCode, locations.locationName, bays.bayName;
                                """

            try:
                database.cursor.execute(details_sql, (current_record,))
                details = database.cursor.fetchall()

                database.cursor.execute(line_items_sql, (current_record,))
                line_items = database.cursor.fetchall()
            except Exception as e:
                print(e)
            finally:
                database.disconnect_from_db()

            details_dict = {
                "name": details[0][0],
                "order_number": details[0][1],
                "delivery_date": details[0][2],
            }

            timestamp = datetime.datetime.today()

            filename = f"{folder_path}/{details_dict['order_number']}_pickinglist_{str(timestamp)[0:9]}.pdf"

            try:
                create_picking_list(
                    filename,
                    details_dict,
                    line_items,
                )

                # For Windows
                if os.name == "nt":
                    os.startfile(filename)
                # For macOS
                elif os.name == "posix":
                    os.system(f"open {filename}")
                # For Linux
                else:
                    os.system(f"xdg-open {filename}")
            except Exception as e:
                print(e)
