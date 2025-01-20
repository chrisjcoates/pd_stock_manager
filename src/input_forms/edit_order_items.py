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
        self.lock_complete_rows()

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

        headers = [
            "Name",
            "Product Code",
            "Qty",
            "Qty in stock",
            "ProductID",
            "Picking Status",
            "Order Item ID",
        ]

        self.table.setColumnCount(7)
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
        save_btn.clicked.connect(self.save_order_btn_click)

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
                    SELECT product.productName, product.productCode, 
                    order_item.orderItemQty, stock.stockQty, stock.stockID, 
                    order_item.pickingStatus, order_item.orderItemID
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
            for col_index, cell_data in enumerate(row_data):
                self.table.setItem(
                    row_index, col_index, QTableWidgetItem(str(cell_data))
                )

        combo_items = ["WIP", "Complete"]

        self.table.setRowCount(len(self.items))

        for row_index, row in enumerate(self.items):
            combo = QComboBox()
            combo.addItems(combo_items)

            if row[-1]:
                combo.setCurrentText(row[-2])

            self.table.setCellWidget(row_index, 5, combo)
            self.table.setItem(row_index, 5, QTableWidgetItem(""))

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

        self.save_order()

    def save_order(self):

        database = Database()
        database.connect_to_db()

        current_items = []
        combo_index = 5
        # Loop through rows in table widget, append data to current_items
        try:
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)

                    if col == combo_index:
                        combo = self.table.cellWidget(row, col)
                        if isinstance(combo, QComboBox):
                            row_data.append(combo.currentText())
                    else:
                        row_data.append(item.text() if item else "")

                current_items.append(tuple(row_data))
        except Exception as e:
            print(f"save_order() 'looping through current_items': {e}")

        [print(row) for row in enumerate(current_items)]

        try:
            for row in current_items:
                order_item_id = row[6]
                new_item_qty = int(row[2])
                refill_qty = 0

                if order_item_id != "":
                    try:
                        # Fetch existing order item
                        database.cursor.execute(
                            """
                        SELECT * FROM order_item WHERE orderItemID = %s
                        """,
                            (order_item_id,),
                        )
                        existing_item = database.cursor.fetchone()

                        # get qty to put back in stock if qty has changed
                        if existing_item[3] > new_item_qty:
                            refill_qty = existing_item[3] - new_item_qty
                        elif existing_item[3] < new_item_qty:
                            refill_qty = new_item_qty - existing_item[3]
                        print(f"Refill Qty: {refill_qty}")
                    except Exception as e:
                        print(f"error here {e}")

                # Update stock qty for item qty change
                if refill_qty > 0 and row[5] == "Complete":
                    # Check if stock needs adding or removing
                    if existing_item[3] > new_item_qty:
                        # Put qty back into stock
                        database.cursor.execute(
                            """UPDATE stock
                                SET stockQty = stockQty + %s
                                WHERE stockID = %s;""",
                            (refill_qty, row[4]),
                        )
                        database.conn.commit()
                        print("Stock qty put back into stock")
                    elif existing_item[3] < new_item_qty:
                        # Remove qty from stock
                        database.cursor.execute(
                            """UPDATE stock
                                SET stockQty = stockQty - %s
                                WHERE stockID = %s;""",
                            (refill_qty, row[4]),
                        )
                        database.conn.commit()
                        print("Stock qty removed from stock")

                if row[6] != "":
                    database.cursor.execute(
                        """
                    UPDATE order_item
                    SET orderItemQty = %s, pickingStatus = %s
                    WHERE orderItemID = %s;
                    """,
                        (row[2], row[5], order_item_id),
                    )
                    database.conn.commit()
                    print("row updated")
                else:
                    database.cursor.execute(
                        """
                    INSERT INTO order_item (orderID, stockID, orderItemQty, pickingStatus)
                    VALUES (%s, %s, %s)
                    """,
                        (self.record_id, row[4], row[2], row[5]),
                    )
                    database.conn.commit()
                    print("row inserted")

        except Exception as e:
            print(f"save_order() 'Executing database query': {e}")
        finally:
            database.disconnect_from_db()

        # DELETE removed line items
        delete_sql = """
                        DELETE FROM order_item
                        WHERE orderItemID = %(order_item_id)s;
                    """

    def remove_item(self):

        selected_row = self.table.currentRow()

        if selected_row < len(self.items):
            try:
                removed_row = self.items.pop(selected_row)
                self.removed_items.append(removed_row)
                self.table.removeRow(selected_row)
            except Exception as e:
                print(f"No items to remove: {e}")
        else:
            # Work out index for additional items list
            index = selected_row - len(self.items)

            try:
                removed_row = self.additional_items.pop(index)
                self.removed_items.append(removed_row)
                self.table.removeRow(selected_row)
            except Exception as e:
                print(f"No items to remove: {e}")

    def lock_complete_rows(self):

        # Loop through table rows
        for row in range(self.table.rowCount()):
            # get the combo box
            combo_box_item = self.table.cellWidget(row, 5)

            if isinstance(combo_box_item, QComboBox):
                # check if the combo box value is complete
                if combo_box_item.currentText() == "Complete":
                    # loop through the columns of the table
                    for column in range(self.table.columnCount()):
                        # lock the row
                        self.table.item(row, 2).setFlags(Qt.ItemFlag.NoItemFlags)
                    # lock the combo box
                    combo_box_item.setEnabled(False)
