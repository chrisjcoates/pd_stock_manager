from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout
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
        self.create_table_widget()
        self.refresh_table()

        
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
        

    def create_table_widget(self):
        # Create table widget
        self.table_widget = QTableWidget(self)
        self.page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(self._row_count)
        self.table_widget.setColumnCount(self._column_count)
        # Set table column header labels
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Qty", "Re-Order", "Supplier", "Location", "Bay"])


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



        