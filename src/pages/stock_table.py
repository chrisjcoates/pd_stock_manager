from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt
from database.database import Database

class StockTable(QWidget):
    def __init__(self):
        super().__init__()

        self.page_layout = QVBoxLayout(self)
        self._database = Database()

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0
        self.data = self._database.get_stock_data()
        self.update_row_column_count()

        # Add widgets to layout
        self.create_button_widgets()
        self.create_text_filter_widget()
        self.create_table_widget()

        
    def create_button_widgets(self):
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)

        add_button = QPushButton(text="Add")
        edit_button = QPushButton(text="Edit")
        delete_button = QPushButton(text="Delete")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        self.page_layout.addWidget(button_widget)

    def create_text_filter_widget(self):
        
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        filter_text_edit = QLineEdit()
        filter_btn= QPushButton(text="Filter")
        clear_filter_btn = QPushButton(text="Clear")

        filter_layout.addWidget(filter_text_edit)
        filter_layout.addWidget(filter_btn)
        filter_layout.addWidget(clear_filter_btn)

        self.page_layout.addWidget(filter_widget)

        def filter_data():
            if filter_text_edit:
                filtered_data = [row for row in self.data if filter_text_edit.text() in row]
                self.data = filtered_data

        

    def create_table_widget(self):
        # Create table widget
        self.table_widget = QTableWidget(self)
        self.page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(self._row_count)
        self.table_widget.setColumnCount(self._column_count)
        # Set table column header labels
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Description", "Qty", "Re-Order", "Supplier", "Location", "Bay", "Value"])

        # Get the table header and set a click event to it
        self.header = self.table_widget.horizontalHeader()
        self.header.sectionClicked.connect(self.on_header_click)

    def on_header_click(self, section_index):
        print(self.table_widget.horizontalHeaderItem(section_index).text())


    def refresh_table(self):
        self.data = self._database.get_stock_data()
        # Add data to table
        for row_index, row_data in enumerate(self.data):
            for col_index, cell_data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))

    def update_row_column_count(self):
        self._row_count = len(self.data)
        for row in self.data:
            for column in row:
                self._column_count += 1
            break



        