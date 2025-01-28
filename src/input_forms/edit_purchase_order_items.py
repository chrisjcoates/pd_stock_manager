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
from datetime import datetime


class EditPurchaseOrderItems(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Edit purchase order")
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
        self.sage_input.setPlaceholderText("Enter PO number")

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
        layout.addRow("Purchase Order No: ", self.sage_input)
        layout.addRow("Delivery Date:", self.date_input)
        layout.addRow("", QLabel())
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
            "Stock ID",
            "Delivery Status",
            "Line Item ID",
        ]

        self.table.setColumnCount(7)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 75)
        self.table.setColumnWidth(4, 75)
        self.table.setColumnWidth(5, 105)
        self.table.setColumnWidth(6, 75)

        self.table.hideColumn(4)
        self.table.hideColumn(6)

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
                    SELECT purchase_orders.purchaseOrderNumber, purchase_orders.deliveryDate
                    FROM purchase_orders
                    WHERE purchaseOrderID = %(order_id)s;
                    """

        arg = {"order_id": self.record_id}

        data = Database().custom_query(sql_query, arg)

        self.sage_input.setText(str(data[0][0]))
        self.date_input.setDate(data[0][1])

    def get_order_items(self, order_id):

        sql_query = """
                    SELECT product.productName, product.productCode, 
                    po_line_items.qtyOrdered, stock.stockQty, stock.stockID, 
                    po_line_items.deliveryStatus, po_line_items.poLineItemID
                    FROM po_line_items
                    INNER JOIN stock ON stock.stockID = po_line_items.stockID
                    INNER JOIN product ON product.productID = stock.productID
                    WHERE po_line_items.purchaseOrderID = %(order_id)s;
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

        self.update_po_line_item_status()

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

        # Loop through each row in current items and update / insert rows to database
        try:
            for row in current_items:
                order_item_id = row[6]

                if row[5] == "Complete":
                    # Add qty to stock
                    database.cursor.execute(
                        """UPDATE stock
                            SET stockQty = stockQty + %s
                            WHERE stockID IN (
                                SELECT stockID
                                FROM po_line_items
                                WHERE stockID = %s AND addedToStock = FALSE);
                                UPDATE po_line_items
                                SET addedToStock = TRUE
                                WHERE stockID = %s AND addedToStock = FALSE;
                            """,
                        (row[2], row[4], row[4]),
                    )
                    database.conn.commit()
                    print("Stock qty removed from stock")

                # If orderItemID exists then there is a current order item to update
                if row[6] != "":
                    database.cursor.execute(
                        """
                    UPDATE po_line_items
                    SET qtyOrdered = %s, deliveryStatus = %s
                    WHERE poLineItemID = %s;
                    """,
                        (row[2], row[5], order_item_id),
                    )
                    database.conn.commit()
                    print("row updated")
                else:  # Else insert a new row into the table
                    database.cursor.execute(
                        """
                    INSERT INTO po_line_items (purchaseOrderID, stockID, qtyOrdered, deliveryStatus)
                    VALUES (%s, %s, %s, %s)
                    """,
                        (self.record_id, row[4], row[2], row[5]),
                    )
                    database.conn.commit()
                    print("row inserted")

            # DELETE removed line items
            if self.removed_items:
                for row in self.removed_items:
                    print(row)
                    if row[6] != "":
                        # Delete the row from the table
                        database.cursor.execute(
                            """
                            DELETE FROM po_line_items
                            WHERE poLineItemID = %s;
                            """,
                            (row[6],),
                        )
                        database.conn.commit()
                        print("row deleted")

                        # check if item qty > 0
                        if row[2] > 0 and row[5] == "Complete":
                            # if so, remove the order item qty from stock
                            database.cursor.execute(
                                """
                                UPDATE stock
                                SET stockQty = stockQty - %s
                                WHERE stockID = %s;
                                """,
                                (row[2], row[4]),
                            )
                            database.conn.commit()
                            print("stock qty updated")

        except Exception as e:
            print(f"save_order() 'Executing database query': {e}")
            msg = QMessageBox(self)
            msg.setText(f"Error updating picking list record, {e}")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.close()
        finally:
            database.disconnect_from_db()
            self.update_picking_list_timestamp()
            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("Picking list record has been updated.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.close()

    def remove_item(self):

        selected_row = self.table.currentRow()

        if selected_row < len(self.items):
            try:
                item_status = self.items[selected_row][5]
                removed_row = self.items.pop(selected_row)
                if item_status == "Complete":
                    self.removed_items.append(removed_row)
                self.table.removeRow(selected_row)
            except Exception as e:
                print(f"No items to remove: {e}")
        else:
            # Work out index for additional items list
            index = selected_row - len(self.items)
            item_status = self.additional_items[index][5]

            try:
                removed_row = self.additional_items.pop(index)
                if item_status == "Complete":
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

    def update_po_line_item_status(self):

        update_flag = True

        # Get the current orderStatus
        database = Database()
        database.connect_to_db()

        order_status_sql = """SELECT purchaseOrderStatus FROM purchase_orders WHERE purchaseOrderID = %s;"""

        # Get the current order status
        try:
            database.cursor.execute(order_status_sql, (self.record_id,))
            order_status = database.cursor.fetchone()
        except Exception as e:
            print(f"update_po_line_item_status(): {e}")
        finally:
            database.disconnect_from_db()

        # Get he picking status for each line item
        database = Database()
        database.connect_to_db()

        select_sql = """SELECT deliveryStatus
                        FROM po_line_items
                        WHERE poLineItemID = %s;"""

        try:
            database.cursor.execute(select_sql, (self.record_id,))
            data = database.cursor.fetchall()
        except Exception as e:
            print(f"update_po_line_item_status(): {e}")
        finally:
            database.disconnect_from_db()

        # Loop though the status' and update flag if status is WIP
        if data:
            for record in data:
                if record[0] == "WIP":
                    update_flag = False
                    break

            # If update flag is False update the orderStatus to 'Complete'
            if update_flag:
                database = Database()
                database.connect_to_db()

                update_sql = """UPDATE purchase_orders
                                SET purchaseOrderStatus = 'Complete'
                                WHERE purchaseOrderID = %s;"""

                try:
                    database.cursor.execute(update_sql, (self.record_id,))
                except Exception as e:
                    print(f"update_po_line_item_status(): {e}")
                finally:
                    database.conn.commit()
                    database.disconnect_from_db()

        # If order status is complete, but line item status is WIP update order status to WIP
        if order_status:
            if order_status[0] == "Complete":
                if data:
                    for record in data:
                        if record[0] == "WIP":

                            database = Database()
                            database.connect_to_db()

                            update_sql = """UPDATE purchase_orders
                                            SET purchaseOrderStatus = 'WIP'
                                            WHERE purchaseOrderID = %s;"""

                            try:
                                database.cursor.execute(update_sql, (self.record_id,))
                            except Exception as e:
                                print(f"update_po_line_item_status(): {e}")
                            finally:
                                database.conn.commit()
                                database.disconnect_from_db()

    def update_picking_list_timestamp(self):

        database = Database()
        database.connect_to_db()

        timestamp = datetime.now()

        update_sql = """UPDATE purchase_orders
                        SET dateUpdated = %s
                        WHERE purchaseOrderID = %s;"""

        try:
            database.cursor.execute(update_sql, (timestamp, self.record_id))
            database.conn.commit()
        except Exception as e:
            print(f"update_picking_list_timestamp(): {e}")
        finally:
            database.disconnect_from_db()
