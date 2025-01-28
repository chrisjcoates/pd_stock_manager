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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from database.database import Database
from popup_boxes.delete_product import DeletePopup
from classes.functions import export_array_to_excel
from input_forms.add_purchase_order import AddPurchaseOrderWindow
from input_forms.edit_purchase_order_items import EditPurchaseOrderItems


class PurchaseOrdersTable(QWidget):
    def __init__(self):
        super().__init__()

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

        select_sql = """SELECT 
                        purchaseOrderID, 
                        purchaseOrderNumber, 
                        TO_CHAR(deliveryDate, 'DD/MM/YYYY'), 
                        purchaseOrderStatus, 
                        TO_CHAR(dateCreated, 'DD/MM/YYYY'), 
                        TO_CHAR(dateUpdated, 'DD/MM/YYYY')
                        FROM purchase_orders
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

        self.table_widget.setRowCount(len(self.data))

        if self.data:
            for row_index, row_data in enumerate(self.data):
                for col_index, col_data in enumerate(row_data):
                    self.table_widget.setItem(
                        row_index, col_index, QTableWidgetItem(str(col_data))
                    )

        self.format_cells()

    def create_button_widgets(self):
        """Create button widgets"""
        # Create button widgets
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        # Create buttons
        add_button = QPushButton(text="Add Purchase Order")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")
        export_btn = QPushButton(text="Export data")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(export_btn)

        # button binds
        add_button.clicked.connect(self.open_add_product_form)
        edit_button.clicked.connect(self.open_edit_product_form)
        # delete_button.clicked.connect(self.delete_picking_list)
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
        header_labels = [
            "ID",
            "PO No.",
            "Delivery Date",
            "Delivery Status",
            "Date Created",
            "Last Edit",
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
        self.table_widget.setColumnWidth(2, 250)
        self.table_widget.setColumnWidth(3, 200)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 200)
        self.table_widget.setColumnWidth(6, 200)

    def open_add_product_form(self):

        def update_table():
            self.refresh_table()
            self.add_product_form.destroy()

        """Opens the add product input form
        and adds close event signal to update the table data
        """
        # Creates the product input form
        self.add_product_form = AddPurchaseOrderWindow()
        # Create an on close signal event to refresh the table data
        self.add_product_form.closed_signal.connect(update_table)
        # Open the input form
        self.add_product_form.show()

    def open_edit_product_form(self):

        def update_table():
            self.update_table_data()
            self.add_product_form.destroy()

        """Opens the edit product input form
        and adds close event signal to update the table data
        """
        try:
            # Get the id of the current selected record
            current_record = self.current_record_selected()
            # Creates the product input form
            self.add_product_form = EditPurchaseOrderItems(current_record)
            # Create an on close signal event to refresh the table data
            self.add_product_form.closed_signal.connect(update_table)
            # Open the input form
            self.add_product_form.show()
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

    def format_cells(self):
        # Loop through each row in the table widget
        for row in range(self.table_widget.rowCount()):
            # set the qty / reorder fields as variables
            status_field = self.table_widget.item(row, 3)

            # check is the qty and reorder have values
            if status_field.text() == "WIP":
                status_field.setBackground(QColor(250, 243, 30))
            else:
                # Set cell colour to default
                status_field.setBackground(QColor(113, 191, 114))
