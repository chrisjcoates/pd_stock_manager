from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QHeaderView,
    QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from database.database import Database
from input_forms.add_product import AddProduct
from input_forms.edit_product import EditProduct
from popup_boxes.delete_product import DeletePopup
from classes.functions import export_array_to_excel


class OrdersTable(QWidget):
    def __init__(self):
        super().__init__()

        self.page_layout = QVBoxLayout(self)

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0
        # Set the database object
        self._database = Database()
        self.data = self._database.get_stock_data()
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
        add_button = QPushButton(text="Create Order")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")
        export_btn = QPushButton(text="Export data")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(export_btn)

        # button binds
        # add_button.clicked.connect(self.open_add_product_form)
        # edit_button.clicked.connect(self.open_edit_product_form)
        # delete_button.clicked.connect(self.delete_product)
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
                "User",
                "Date Created",
                "Last Edit",
            ]
        )

        # Get the table header and set a click event to it
        self.header = self.table_widget.horizontalHeader()
        self.header.sectionClicked.connect(self.on_header_click)
        # Set the table column widths
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.setColumnWidth(2, 250)
        self.table_widget.setColumnWidth(3, 200)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 200)

    def on_header_click(self, section_index):
        pass

    def refresh_table(self, filter=None):
        """refreshes the table data by querying the database to get the most upto data data"""
        # Update to db connection to current settings
        self._database.update_db_connection()
        if filter == None:
            # set data to the most recent data
            self.data = self._database.get_orders_data()
            print("Data retrieved")
            # update the row and column count
            self.update_row_column_count()
        # Add data to table
        try:
            # Loop though data and add data to table
            for row_index, row_data in enumerate(self.data):
                for col_index, cell_data in enumerate(row_data):
                    self.table_widget.setItem(
                        row_index, col_index, QTableWidgetItem(str(cell_data))
                    )
        except Exception as e:
            print(e)

        # self.format_qty_cells()

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
                self.table_widget.setRowCount(self._row_count)
                self.table_widget.setColumnCount(self._column_count)
            else:
                no_data = True
        except Exception as e:
            print(e)

        if no_data:
            self._row_count = 0
            self._column_count = 5

    def open_add_product_form(self):

        def update_table():
            self.refresh_table()
            self.add_product_form.destroy()

        """Opens the add product input form
        and adds close event signal to update the table data
        """
        # Creates the product input form
        self.add_product_form = AddProduct()
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
        # Get the id of the current selected record
        current_record = self.current_record_selected()
        print(current_record)
        # Creates the product input form
        self.add_product_form = EditProduct(current_record)
        # Create an on close signal event to refresh the table data
        self.add_product_form.closed_signal.connect(update_table)
        # Open the input form
        self.add_product_form.show()

    def delete_product(self):

        def update_table():
            self.refresh_table()
            self.delete_popup.destroy()

        # Get the id of the current selected record
        current_record = self.current_record_selected()
        # Creates the product input form
        self.delete_popup = DeletePopup(current_record)
        # Create an on close signal event to refresh the table data
        self.delete_popup.closed_signal.connect(update_table)
        # Open the input form
        self.delete_popup.show()

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
            qty_field = self.table_widget.item(row, 5)
            reorder_field = self.table_widget.item(row, 6)
            # check is the qty and reorder have values
            if qty_field and reorder_field:
                try:
                    # Set the fields values to ints
                    qty = int(qty_field.text())
                    reorder = int(reorder_field.text())
                    # Check if qty =< reorder
                    if qty <= reorder:
                        # Set cell colour to red
                        qty_field.setBackground(QColor(227, 127, 127))
                    else:
                        # Set cell colour to default
                        qty_field.setBackground(QColor(113, 191, 114))
                except Exception as e:
                    print(e)
                    # Set cell colour to default
                    qty_field.setBackground(QColor(113, 191, 114))
