from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
)
from PySide6.QtCore import Qt
from database.database import Database


class Add_Items_Window(QWidget):
    def __init__(self):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()

        self.get_customers()

    def order_details_widget(self):

        # Main widget layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # input widget layout
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.setLabelAlignment(Qt.AlignLeft)

        # button widget layout
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setAlignment(Qt.AlignBottom)

        # control widgets
        sage_input = QLineEdit()
        self.cust_input = QComboBox()

        type_combo = QComboBox()
        item_combo = QComboBox()

        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Remove")

        # Add widgets to layout
        layout.addRow("Sage No.", sage_input)
        layout.addRow("Customer:", self.cust_input)
        layout.addRow("Type:", type_combo)
        layout.addRow("Item:", item_combo)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)

        main_layout.addWidget(widget)
        main_layout.addWidget(btn_widget)

        # Add main widget to main window
        self.window_layout.addWidget(main_widget)

    def item_table_widget(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        table = QTableWidget()

        headers = ["ID", "Name", "Qty"]
        table.setColumnCount(3)
        table.setRowCount(0)
        table.setHorizontalHeaderLabels(headers)

        layout.addWidget(table)

        self.window_layout.addWidget(widget)

    def save_btn_widget(self):

        widget = QWidget()
        layout = QHBoxLayout(widget)

        save_btn = QPushButton("Save & Exit")

        layout.addWidget(save_btn)

        self.window_layout.addWidget(widget)

    def get_customers(self):

        data = None

        sql_query = """
                    SELECT customerID, customerName 
                    FROM customer;
                    """

        data = Database().custom_query(sql_query)

        for id, name in data:
            self.cust_input.addItem(name, userData=id)


# app = QApplication([])
# window = Add_Items_Window()
# window.show()
# app.exec()
