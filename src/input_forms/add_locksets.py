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


class AddLockSets(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_style_path())

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Create a new lock set")
        self.setWindowModality(Qt.ApplicationModal)

        self.order_details_widget()
        self.save_btn_widget()

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
        self.lockset_name = QLineEdit()
        self.lockset_name.setFixedWidth(175)
        self.lockset_name.setPlaceholderText("Enter location name")

        ######################
        # Lock drop down box #
        ######################

        locks_sql = """
                        SELECT
                            product.productID,
                            product.productName
                        FROM product
                        WHERE product.prod_cat_ID = (
                            SELECT prod_cat_id from product_categories WHERE prod_CatName = 'Lock'
                        );
                    """

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(locks_sql)
            combo_data = database.cursor.fetchall()
        except Exception as e:
            print(f"locks_sql: {e}")
        finally:
            database.disconnect_from_db()

        self.lock_id = QComboBox()
        self.lock_id.setPlaceholderText("Select Lock")
        self.lock_id.setFixedWidth(175)
        for id, name in combo_data:
            self.lock_id.addItem(name, userData=id)

        #####################
        # Int drop down box #
        #####################

        int_sql = """
                        SELECT
                            product.productID,
                            product.productName
                        FROM product
                        WHERE product.prod_cat_ID = (
                            SELECT prod_cat_id from product_categories WHERE prod_CatName = 'Intumescent'
                        );
                    """

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(int_sql)
            combo_data = database.cursor.fetchall()
        except Exception as e:
            print(f"int_sql: {e}")
        finally:
            database.disconnect_from_db()

        self.intumescent_id = QComboBox()
        self.intumescent_id.setPlaceholderText("Select intumescent")
        self.intumescent_id.setFixedWidth(175)
        for id, name in combo_data:
            self.intumescent_id.addItem(name, userData=id)

        ########################
        # Handle drop down box #
        ########################

        handle_sql = """
                        SELECT
                            product.productID,
                            product.productName
                        FROM product
                        WHERE product.prod_cat_ID = (
                            SELECT prod_cat_id from product_categories WHERE prod_CatName = 'Handle'
                        );
                    """

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(handle_sql)
            combo_data = database.cursor.fetchall()
        except Exception as e:
            print(f"handle_sql: {e}")
        finally:
            database.disconnect_from_db()

        self.handle_id = QComboBox()
        self.handle_id.setPlaceholderText("Select handle")
        self.handle_id.setFixedWidth(175)
        for id, name in combo_data:
            self.handle_id.addItem(name, userData=id)

        ##########################
        # Cylinder drop down box #
        ##########################

        cylinder_sql = """
                        SELECT
                            product.productID,
                            product.productName
                        FROM product
                        WHERE product.prod_cat_ID = (
                            SELECT prod_cat_id from product_categories WHERE prod_CatName = 'Cylinder'
                        );
                    """

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(cylinder_sql)
            combo_data = database.cursor.fetchall()
        except Exception as e:
            print(f"cylinder_sql: {e}")
        finally:
            database.disconnect_from_db()

        self.cylinder_id = QComboBox()
        self.cylinder_id.setPlaceholderText("Select cylinder")
        self.cylinder_id.setFixedWidth(175)
        for id, name in combo_data:
            self.cylinder_id.addItem(name, userData=id)

        ############################
        # Escutcheon drop down box #
        ############################

        escutcheon_sql = """
                        SELECT
                            product.productID,
                            product.productName
                        FROM product
                        WHERE product.prod_cat_ID = (
                            SELECT prod_cat_id from product_categories WHERE prod_CatName = 'Escutcheon'
                        );
                    """

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(escutcheon_sql)
            combo_data = database.cursor.fetchall()
        except Exception as e:
            print(f"escutchoen_sql: {e}")
        finally:
            database.disconnect_from_db()

        self.escutcheon_id = QComboBox()
        self.escutcheon_id.setPlaceholderText("Select escutcheon")
        self.escutcheon_id.setFixedWidth(175)
        for id, name in combo_data:
            self.escutcheon_id.addItem(name, userData=id)

        # Add widgets to layout
        layout.addRow("Name: ", self.lockset_name)
        layout.addRow("Lock:", self.lock_id)
        layout.addRow("Intumescent Kit:", self.intumescent_id)
        layout.addRow("Handle:", self.handle_id)
        layout.addRow("Cylinder:", self.cylinder_id)
        layout.addRow("Escutcheons: ", self.escutcheon_id)

        main_layout.addWidget(widget)
        main_layout.addWidget(btn_widget)

        # Add main widget to main window
        self.window_layout.addWidget(main_widget)

    def save_btn_widget(self):

        widget = QWidget()
        layout = QHBoxLayout(widget)

        save_btn = QPushButton("Save & Exit")
        save_btn.clicked.connect(self.save_order_btn_click)

        layout.addWidget(save_btn)

        self.window_layout.addWidget(widget)

    def save_order_btn_click(self):

        self.save_order()

        self.close()

    def save_order(self):

        lockset_name = self.lockset_name.text()
        lock_id = self.lock_id.currentData()
        int_kit_id = self.intumescent_id.currentData()
        handle_id = self.handle_id.currentData()
        cylinder_id = self.cylinder_id.currentData()
        escutchon_id = self.escutcheon_id.currentData()

        insert_sql = """
                        INSERT INTO lock_sets (lock_set_name, lock_id, intumescent_id, handle_id, cylinder_id, escutcheon_id)
                        VALUES (%s,%s,%s,%s,%s,%s);
                    """

        try:
            database = Database()
            database.connect_to_db()

            database.cursor.execute(
                insert_sql,
                (
                    lockset_name,
                    lock_id,
                    int_kit_id,
                    handle_id,
                    cylinder_id,
                    escutchon_id,
                ),
            )
            database.conn.commit()
        except Exception as e:
            database.conn.rollback()
            print(f"save_order(): {e}")
        finally:
            database.disconnect_from_db()
