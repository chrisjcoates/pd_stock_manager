from PySide6.QtWidgets import (
    QCheckBox,
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
from PySide6.QtCore import Qt, QDate, Signal
from database.database import Database
from classes.functions import get_style_path


class Add_Items_Window(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_style_path())

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Create new picking list")
        self.setWindowModality(Qt.ApplicationModal)

        self.items = []

        self.order_details_widget()
        self.item_table_widget()
        self.save_btn_widget()
        self.lock_selected_cells()
        self.get_customers()
        self.get_types()
        self.get_items(prod_cat_id=self.type_combo.currentData())

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

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())

        self.cust_input = QComboBox()
        self.cust_input.setPlaceholderText("Select a customer")
        self.cust_input.setFixedWidth(200)

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(200)
        self.type_combo.setPlaceholderText("Select a type")
        self.type_combo.currentIndexChanged.connect(
            lambda: self.get_items(self.type_combo.currentData())
        )
        self.item_combo = QComboBox()
        self.item_combo.setFixedWidth(350)
        self.item_combo.setPlaceholderText("Select an item")
        self.lock_set_check = QCheckBox()

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
        layout.addRow("Add as a lock set? ", self.lock_set_check)

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

        headers = ["Name", "Product Code", "Qty", "Qty in stock"]

        self.table.setColumnCount(5)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 75)

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
                    FROM product_categories
                    ORDER BY prod_catName;
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
        if not self.lock_set_check.isChecked():
            # Set sql query
            sql_query = """
                        SELECT product.productName, product.productCode, stock.stockQty, stock.stockID
                        FROM product
                        INNER JOIN stock ON product.productID = stock.productID
                        WHERE product.productID = %(id)s;
                        """
            # Set query argument
            arg = {"id": prod_cat_id}
            # run query
            data = Database().custom_query(sql_query, arg)
            # create item
            item = (data[0][0], data[0][1], 0, data[0][2], data[0][3])
            # add item to items list
            self.items.append(item)
            # Add item to table
            row_position = self.table.rowCount()
            # insert new row
            self.table.insertRow(row_position)
            # add data to that row
            for column, data in enumerate(item):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row_position, column, item)
        else:
            items = self.add_as_lock_set(prod_cat_id)
            print(items)
            if items == None:
                msg = QMessageBox(self)
                msg.setText(f"No Lock set found for the selected item.")
                msg.setWindowTitle("Message")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            else:
                for item in items:
                    row = (item[0], item[1], 0, item[2], item[3], "", "WIP")
                    self.items.append(row)
                    # Gte row count
                    row_position = self.table.rowCount()
                    # insert new row
                    self.table.insertRow(row_position)
                    # add data to that row
                    for column, data in enumerate(row[0:-1]):
                        item = QTableWidgetItem(str(data))
                        self.table.setItem(row_position, column, item)

                    combo_items = ["WIP", "Complete"]
                    combo = QComboBox()
                    combo.addItems(combo_items)
                    combo.setCurrentText("WIP")
                    self.table.setCellWidget(row_position, 5, combo)

        self.lock_set_check.setChecked(False)

    def save_order_btn_click(self):

        if self.sage_input.text() or self.cust_input.text():
            self.save_order()
        else:
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText(
                "You need to enter a Sage number and customer name to be able to create an order."
            )
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        self.close()

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
        delivery_date = self.date_input.date().toString("MM-dd-yyyy")

        # create dict for order table record
        order_dict = {
            "sage_number": sage_number,
            "cust_id": cust_id,
            "user_id": 1,
            "delivery_date": delivery_date,
        }

        # Insert into order table
        sql_query = """
                    INSERT INTO orders (sageNumber, customerID, userID, deliveryDate)
                    VALUES (%(sage_number)s, %(cust_id)s, %(user_id)s, %(delivery_date)s)
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

        try:
            self.items.pop(selected_row)
            self.table.removeRow(selected_row)
        except:
            print("No items to remove.")

    def add_as_lock_set(self, item_id):

        lock_set = {"lock_id": 0, "intumescent_id": 0, "handle_id": 0, "cylinder_id": 0}

        # Check if item ID is in the lock_sets table
        database = Database()
        database.connect_to_db()

        check_for_item_sql = """SELECT lock_id, intumescent_id, handle_id, cylinder_id FROM lock_sets WHERE lock_id = %s;"""
        try:
            database.cursor.execute(check_for_item_sql, (item_id,))
            result = database.cursor.fetchone()

            if result:  # Check if a result is found
                row = [
                    id_value if id_value is not None and id_value > 0 else 0
                    for id_value in result
                ]  # Ensure no None values
                for key, id_value in zip(lock_set.keys(), row):
                    lock_set[key] = id_value
            else:
                result = []

        except Exception as e:
            print(f"add_as_lock_set(): first query - {e}")
            result = []

        # If a lock set is found
        if result:
            lock_set_items_sql = """
                SELECT product.productName, product.productCode, stock.stockQty, stock.stockID
                FROM product
                INNER JOIN stock ON product.productID = stock.productID
                WHERE product.productID = %s;
            """

            items = []
            for key, value in lock_set.items():
                if value:
                    try:
                        database.cursor.execute(lock_set_items_sql, (value,))
                        items.append(database.cursor.fetchone())
                    except Exception as e:
                        print(f"add_as_lock_set(): second query - {e}")

            if items:
                return items
            else:
                return False

    def lock_selected_cells(self):
        for row in range(self.table.rowCount()):
            for col in range(2):
                self.table.item(row, col).setFlags(Qt.ItemFlag.NoItemFlags)
                self.table.item(row, col).setFlags(Qt.ItemFlag.NoItemFlags)
