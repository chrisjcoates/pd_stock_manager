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
    QTableWidgetItem,
)
from PySide6.QtCore import Qt
from database.database import Database


class Add_Items_Window(QWidget):
    def __init__(self):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.items = []
        self.add_item()

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()

        self.get_customers()
        self.get_types()
        self.get_items(prod_cat_id=self.type_combo.currentData())

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

        self.type_combo = QComboBox()
        self.type_combo.currentIndexChanged.connect(
            lambda: self.get_items(self.type_combo.currentData())
        )
        self.item_combo = QComboBox()

        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Remove")

        # Add widgets to layout
        layout.addRow("Sage No.", sage_input)
        layout.addRow("Customer:", self.cust_input)
        layout.addRow("Type:", self.type_combo)
        layout.addRow("Item:", self.item_combo)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)

        main_layout.addWidget(widget)
        main_layout.addWidget(btn_widget)

        # Add main widget to main window
        self.window_layout.addWidget(main_widget)

    def item_table_widget(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.table = QTableWidget()

        headers = ["ID", "Name", "Product Code", "Qty", "Qty in stock"]
        self.table.setColumnCount(5)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 100)

        layout.addWidget(self.table)

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

    def get_types(self):

        data = None

        sql_query = """
                    SELECT prod_cat_id, prod_catName
                    FROM product_categories;
                    """

        data = Database().custom_query(sql_query)

        for id, name in data:
            self.type_combo.addItem(name, userData=id)

    def get_items(self, prod_cat_id):

        data = None

        sql_query = """
                    SELECT DISTINCT productID, productName || ', ' || productCode
                    FROM product
                    WHERE prod_cat_id = %(id)s;
                    """

        arg = {"id": prod_cat_id}

        data = Database().custom_query(sql_query, arg)

        self.item_combo.clear()

        for id, name in data:
            self.item_combo.addItem(name)

    def add_item(self):
        pass


# app = QApplication([])
# window = Add_Items_Window()
# window.show()
# app.exec()
