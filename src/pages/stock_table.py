from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class StockTable(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QVBoxLayout(self)
        _row_count = 0
        _column_count = 0

        self.table_widget = QTableWidget(self)
        page_layout.addWidget(self.table_widget)
        self.table_widget.setRowCount(5)
        self.table_widget.setColumnCount(3)

        self.table_widget.setHorizontalHeaderLabels(["Name", "Age", "City"])

        data = [
            ("Chris", "35", "Darwen"),
            ("Chris", "35", "Darwen"),
            ("Chris", "35", "Darwen"),
        ]

        for row_index, row_data in enumerate(data):
            for col_index, cell_data in enumerate(row_data):
                self.table_widget.setItem(row_index, col_index, QTableWidgetItem(cell_data))

    def update_row_column_count(self):
        pass



        