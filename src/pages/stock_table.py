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


class StockTable(QWidget):
    def __init__(self):
        super().__init__()

        self.page_layout = QVBoxLayout(self)

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0

        self._database = Database()
        self.data = self._database.get_stock_data()
        self.update_row_column_count()

        # Add widgets to layout
        self.create_button_widgets()
        self.create_text_filter_widget()
        self.create_table_widget()

    def create_button_widgets(self):
        # Create button widgets
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        # Create buttons
        add_button = QPushButton(text="Add")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")
        # Add buttons to layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        self.page_layout.addWidget(button_widget)

    def create_text_filter_widget(self):

        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        filter_line_edit = QLineEdit()
        filter_widget.setMaximumWidth(500)
        filter_btn = QPushButton(text="Filter")
        clear_filter_btn = QPushButton(text="Clear")

        filter_btn.clicked.connect(lambda: filter_data())
        clear_filter_btn.clicked.connect(lambda: clear_filter())

        filter_layout.addWidget(filter_line_edit)
        filter_layout.addWidget(filter_btn)
        filter_layout.addWidget(clear_filter_btn)

        self.page_layout.addWidget(filter_widget)

        def filter_data():
            filter_text = filter_line_edit.text()
            try:
                if filter_text:
                    filtered_data = [
                        row
                        for row in self.data
                        if any(filter_text.lower() in str(cell).lower() for cell in row)
                    ]
                    self.data = filtered_data
                    self.update_row_column_count(True)
                    self.refresh_table(True)
                    print("Data filtered.")
            except Exception as e:
                print(e)

        def clear_filter():
            try:
                self.data = self._database.get_stock_data()
                self.update_row_column_count(True)
                self.refresh_table(True)
                filter_line_edit.clear()
                print("Data un-filtered.")
            except Exception as e:
                print(e)

    def create_table_widget(self):
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

        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 200)
        self.table_widget.setColumnWidth(2, 200)
        self.table_widget.setColumnWidth(3, 125)
        self.table_widget.setColumnWidth(4, 100)
        self.table_widget.setColumnWidth(5, 100)
        self.table_widget.setColumnWidth(6, 125)

    def on_header_click(self, section_index):
        pass

    def refresh_table(self, filter=False):
        if self._database != None:
            if filter == False:
                self._database.update_db_connection()
                self.data = self._database.get_stock_data()
                print("Data retrieved")
                self.update_row_column_count()
        # Add data to table
        try:
            for row_index, row_data in enumerate(self.data):
                for col_index, cell_data in enumerate(row_data):
                    self.table_widget.setItem(
                        row_index, col_index, QTableWidgetItem(str(cell_data))
                    )
        except Exception as e:
            print(e)

    def update_row_column_count(self, row_column_count=False):
        try:
            self._row_count = len(self.data)
            self._column_count = 0
            for row in self.data:
                for column in row:
                    self._column_count += 1
                break
            if row_column_count:
                self.table_widget.setRowCount(self._row_count)
                self.table_widget.setColumnCount(self._column_count)
        except Exception as e:
            print(e)
