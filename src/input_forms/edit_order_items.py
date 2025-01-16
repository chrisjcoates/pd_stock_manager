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
    QMessageBox,
    QDateEdit,
)
from database.database import Database
from PySide6.QtCore import Qt, Signal, QDate


class Edit_Order_Items(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Create new picking list")
        self.setWindowModality(Qt.ApplicationModal)

        # Current records items
        self.items = []

        # Separate array for new items
        self.additional_items = []

        # Removed items
        self.removed_items = []

        self.record_id = record_id

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()

        self.get_customers()
        self.get_types()
        self.get_items(prod_cat_id=self.type_combo.currentData())
        self.get_order(self.record_id)
        self.get_order_items(self.record_id)

        self.resize(760, 600)

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

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
        self.sage_input = QLineEdit()
        self.sage_input.setPlaceholderText("Enter Sage number")
        self.cust_input = QComboBox()
        self.cust_input.setPlaceholderText("Select a customer")
        self.cust_input.setFixedWidth(200)

        self.date_input = QDateEdit()

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(200)
        self.type_combo.setPlaceholderText("Select a type")
        self.type_combo.currentIndexChanged.connect(
            lambda: self.get_items(self.type_combo.currentData())
        )
        self.item_combo = QComboBox()
        self.item_combo.setFixedWidth(350)
        self.item_combo.setPlaceholderText("Select an item")

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(lambda: self.add_item(self.item_combo.currentData()))
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_item)

        # Add widgets to layout
        layout.addRow("Sage No: ", self.sage_input)
        layout.addRow("Delivery Date:", self.date_input)
        layout.addRow("", QLabel())
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

        headers = ["Name", "Product Code", "Qty", "Qty in stock", "", "Picking Status"]

        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 75)
        self.table.setColumnWidth(5, 105)

        self.table.hideColumn(4)

        layout.addWidget(self.table)

        self.window_layout.addWidget(widget)

    def save_btn_widget(self):

        widget = QWidget()
        layout = QHBoxLayout(widget)

        save_btn = QPushButton("Save & Exit")
        # save_btn.clicked.connect(self.save_order_btn_click)

        layout.addWidget(save_btn)

        self.window_layout.addWidget(widget)

    def get_order(self, id):

        sql_query = """
                    SELECT orders.sageNumber, customer.customerName, orders.deliveryDate
                    FROM orders
                    INNER JOIN customer ON customer.customerID = orders.customerID
                    WHERE orderID = %(order_id)s;
                    """

        arg = {"order_id": self.record_id}

        data = Database().custom_query(sql_query, arg)

        self.sage_input.setText(str(data[0][0]))
        self.cust_input.setCurrentText(str(data[0][1]))
        self.date_input.setDate(data[0][2])

    def get_order_items(self, order_id):

        sql_query = """
                    SELECT product.productName, product.productCode, order_item.orderItemQty, stock.stockQty, product.productID, order_item.pickingStatus
                    FROM order_item
                    INNER JOIN stock ON stock.stockID = order_item.stockID
                    INNER JOIN product ON product.productID = stock.productID
                    WHERE order_item.orderID = %(order_id)s;
                    """

        arg = {"order_id": order_id}

        data = Database().custom_query(sql_query, arg)

        for row in data:
            self.items.append(row)

        self.table.setRowCount(len(self.items))

        for row_index, row_data in enumerate(self.items):
            for col_index, cell_data in enumerate(row_data[0:-1]):
                self.table.setItem(
                    row_index, col_index, QTableWidgetItem(str(cell_data))
                )

        combo_items = ["WIP", "Complete"]

        self.table.setRowCount(len(self.items))

        for row_index, row in enumerate(self.items):
            combo = QComboBox()
            combo.addItems(combo_items)

            if row[-1]:
                combo.setCurrentText(row[-1])

            self.table.setCellWidget(row_index, 5, combo)

    def get_customers(self):

        data = None

        sql_query = """
                    SELECT customerID, customerName 
                    FROM customer;
                    """
        try:
            data = Database().custom_query(sql_query)

            for id, name in data:
                self.cust_input.addItem(name, userData=id)
        except Exception as e:
            print(e)

    def get_types(self):

        data = None

        sql_query = """
                    SELECT prod_cat_id, prod_catName
                    FROM product_categories;
                    """
        try:
            data = Database().custom_query(sql_query)

            for id, name in data:
                self.type_combo.addItem(name, userData=id)
        except Exception as e:
            print(e)

    def get_items(self, prod_cat_id):

        data = None

        sql_query = """
                    SELECT DISTINCT productID, productName || ', ' || productCode
                    FROM product
                    WHERE prod_cat_id = %(id)s;
                    """

        arg = {"id": prod_cat_id}

        try:
            data = Database().custom_query(sql_query, arg)

            self.item_combo.clear()

            for id, name in data:
                self.item_combo.addItem(name, userData=id)
        except Exception as e:
            print(e)

    def add_item(self, prod_cat_id):
        # Set sql query
        sql_query = """
                    SELECT product.productName, product.productCode, stock.stockQty, stock.stockID
                    FROM product
                    INNER JOIN stock ON product.productID = stock.productID
                    WHERE product.productID = %(id)s;
                    """
        # Set query argument
        arg = {"id": prod_cat_id}
        if self.item_combo.currentText():
            # run query
            data = Database().custom_query(sql_query, arg)
            # create item
            item = (data[0][0], data[0][1], 0, data[0][2], data[0][3], "", "WIP")
            # add item to items list
            self.additional_items.append(item)

            # Add item to table
            row_position = self.table.rowCount()
            # insert new row
            self.table.insertRow(row_position)
            # add data to that row
            for column, data in enumerate(item[0:-1]):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row_position, column, item)

            combo_items = ["WIP", "Complete"]
            combo = QComboBox()
            combo.addItems(combo_items)
            combo.setCurrentText("WIP")
            self.table.setCellWidget(row_position, 5, combo)

    def save_order_btn_click(self):

        if self.sage_input.text():
            pass
            # self.save_order()
        else:
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText(
                "You need to enter a Sage number to be able to create an order."
            )
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        if self.cust_input.currentText():
            pass
            # self.save_order()
        else:
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("You need to select a Customer to be able to create an order.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def save_order(self):

        table_array = []

        try:
            for row in range(self.table.rowCount()):
                row_data = tuple(
                    self.table.item(row, col).text()
                    for col in range(self.table.columnCount())
                )
                table_array.append(row_data)

            self.items = table_array
        except:
            pass

        sage_number = self.sage_input.text()
        cust_id = self.cust_input.currentData()

        # create dict for order table record
        order_dict = {"sage_number": sage_number, "cust_id": cust_id, "user_id": 1}

        # Insert into order table
        sql_query = """
                    INSERT INTO orders (sageNumber, customerID, userID)
                    VALUES (%(sage_number)s, %(cust_id)s, %(user_id)s)
                    RETURNING orderID;
                    """

        # Create database object and connect to db
        database = Database()
        database.connect_to_db()

        try:
            # Execute query
            database.cursor.execute(sql_query, order_dict)
            # get order id
            order_id = database.cursor.fetchone()
            order_id = order_id[0]

            # Insert into order item table
            sql_query = """
                        INSERT INTO order_item (orderID, stockID, orderItemQty)
                        VALUES (%(order_id)s, %(stock_id)s, %(order_qty)s);
                        """
            if len(table_array) > 0:
                for row in table_array:
                    stock_id = row[-1]
                    order_qty = row[-3]
                    database.cursor.execute(
                        sql_query,
                        {
                            "order_id": order_id,
                            "stock_id": stock_id,
                            "order_qty": order_qty,
                        },
                    )

        except Exception as e:
            print(f"Error inserting data {e}")

        try:
            database.conn.commit()
        except Exception as e:
            print(e)

        database.disconnect_from_db()

    def remove_item(self):

        selected_row = self.table.currentRow()
        print(selected_row)

        try:
            removed_row = self.items.pop(selected_row)
            self.removed_items.append(removed_row)
            self.table.removeRow(selected_row)
        except Exception as e:
            print(f"No items to remove: {e}")
