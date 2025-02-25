from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from database.database import Database
from input_forms.add_product import AddProduct
from input_forms.edit_product import EditProduct
from popup_boxes.delete_product import DeletePopup
from classes.functions import export_array_to_excel
from classes.functions import get_style_path


class StockTable(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_style_path())

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
        self.create_column_checks()
        self.create_table_widget()

    def create_button_widgets(self):
        """Create button widgets"""
        # Create button widgets
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        # Create buttons
        add_button = QPushButton(text="Add Product")
        edit_button = QPushButton(text="Edit")
        export_btn = QPushButton(text="Export data")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(export_btn)

        # button binds
        add_button.clicked.connect(self.open_add_product_form)
        edit_button.clicked.connect(self.open_edit_product_form)
        export_btn.clicked.connect(self.export_to_excel)

        self.page_layout.addWidget(button_widget)

    def create_text_filter_widget(self):
        # Create filter widget
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # Create filter text box
        filter_line_edit = QLineEdit()
        filter_widget.setMaximumWidth(600)
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
        # create status label
        status_label = QLabel("Show inactive:")
        # create status button
        self.status_btn = QPushButton("Click")
        self.status_btn.clicked.connect(self.show_inactive)

        # Add the widgets rto the layout
        filter_layout.addWidget(filter_line_edit)
        filter_layout.addWidget(filter_btn)
        filter_layout.addWidget(clear_filter_btn)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_btn)
        # Add to main class layout
        self.page_layout.addWidget(filter_widget)

        def filter_data():
            """Function to filter the data based on text input value"""
            # Get filter text
            filter_text = filter_line_edit.text()
            self.data = self._database.get_stock_data()
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

    def create_column_checks(self):

        check_widget = QWidget()
        check_layout = QHBoxLayout(check_widget)

        labels = [
            "Name",
            "Description",
            "Type",
            "Product Code",
            "Supplier",
            "Qty",
            "Allocated",
            "Available",
            "On Order",
            "Reorder",
            "Location",
            "Bay",
            "Value",
        ]
        checkboxes = []

        for label in labels:
            check_layout.addWidget(QLabel(label))
            checkbox = QCheckBox()
            checkbox.setObjectName(label)
            if label != "Reorder":
                checkbox.setChecked(True)
            check_layout.addWidget(checkbox)
            checkboxes.append(checkbox)

        index = 0
        for widget in check_widget.findChildren(QCheckBox):
            if isinstance(widget, QCheckBox):
                widget.clicked.connect(
                    lambda checked, idx=index: self.columns_hide_show(idx)
                )
                index += 1

        self.page_layout.addWidget(check_widget)

    def columns_hide_show(self, column):
        if self.table_widget.isColumnHidden(column + 1):
            self.table_widget.showColumn(column + 1)
        else:
            self.table_widget.hideColumn(column + 1)

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
                "Name",
                "Description",
                "Type",
                "Product Code",
                "Supplier",
                "Qty",
                "Allocated Stock",
                "Stock Available",
                "On Order",
                "Re-Order",
                "Location",
                "Bay",
                "Stock Value",
            ]
        )

        # Set the table column widths
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.setColumnWidth(2, 290)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 150)
        self.table_widget.setColumnWidth(6, 100)
        self.table_widget.setColumnWidth(7, 100)
        self.table_widget.setColumnWidth(8, 100)
        self.table_widget.setColumnWidth(9, 100)
        self.table_widget.setColumnWidth(10, 100)
        self.table_widget.setColumnWidth(11, 100)
        self.table_widget.setColumnWidth(12, 100)
        self.table_widget.setColumnWidth(13, 100)

        self.table_widget.hideColumn(10)

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
                    item = QTableWidgetItem(str(cell_data))
                    self.table_widget.setItem(row_index, col_index, item)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        except Exception as e:
            print(f"refresh_table {e}")
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("No data to filter.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

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
            self._column_count = 12

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
        try:
            # Get the id of the current selected record
            current_record = self.current_record_selected()
            # Creates the product input form
            self.add_product_form = EditProduct(current_record)
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
            qty_field = self.table_widget.item(row, 6)
            reorder_field = self.table_widget.item(row, 10)
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

    def show_inactive(self):

        self.data = Database().get_stock_data(active=False)

        self.update_row_column_count()
        self.refresh_table(filter=True)
