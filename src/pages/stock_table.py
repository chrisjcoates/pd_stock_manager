from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from database.database import Database

class StockTable(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QVBoxLayout(self)
        self._database = Database()

        # Set table attributes & get table data
        self._row_count = 0
        self._column_count = 0
        self.data = self._database.get_stock_data()
        self.update_row_column_count()

        # Create table widget
        self.table_widget = QTableWidget(self)
        page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(self._row_count)
        self.table_widget.setColumnCount(self._column_count)
        # Set table column header labels
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Qty", "Supplier", "Location", "Bay"])

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



        