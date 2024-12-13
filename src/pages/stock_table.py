from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from database.database import Database
from input_forms.add_product import AddProduct


class StockTable(QWidget):
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
        add_button = QPushButton(text="Add Product")
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
                        print(self.data)
            except Exception as e:
                print(e)

        def clear_filter():
            """clears the current filter and returns the table data back to normal"""
            try:
                # get data from database
                self.data = self._database.get_stock_data()
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
        self.page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(self._row_count)
        self.table_widget.setColumnCount(self._column_count)
        # Set table column header labels
        self.table_widget.setHorizontalHeaderLabels(
            [
                "ID",
                "Name",
                "Description",
                "Product Code",
                "Qty",
                "Re-Order",
                "Supplier",
                "Location",
                "Bay",
                "Value",
            ]
        )

        # Get the table header and set a click event to it
        self.header = self.table_widget.horizontalHeader()
        self.header.sectionClicked.connect(self.on_header_click)
        # Set the table column widths
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 200)
        self.table_widget.setColumnWidth(2, 200)
        self.table_widget.setColumnWidth(3, 125)
        self.table_widget.setColumnWidth(4, 100)
        self.table_widget.setColumnWidth(5, 100)
        self.table_widget.setColumnWidth(6, 125)

    def on_header_click(self, section_index):
        pass

    def refresh_table(self, filter=None):
        """refreshes the table data by querying the database to get the most upto data data"""
        # Update to db connection to current settings
        self._database.update_db_connection()
        if filter == None:
            # set data to the most recent data
            self.data = self._database.get_stock_data()
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

    def update_row_column_count(self):
        """updates the row and column count of the table widget"""
        try:
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
        except Exception as e:
            print(e)

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
