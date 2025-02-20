from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
)
from PySide6.QtCore import Qt, QDate, Signal
from database.database import Database


class AddProdCat(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.window_layout = QVBoxLayout(self)

        self.setWindowTitle("Create a Product Category")
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
        self.cat_name = QLineEdit()
        self.cat_name.setFixedWidth(175)
        self.cat_name.setPlaceholderText("Enter product category")

        # Add widgets to layout
        layout.addRow("Name: ", self.cat_name)

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

        insert_sql = """INSERT INTO product_categories (prod_catName) VALUES (%s);"""

        try:
            database = Database()
            database.connect_to_db()
            database.cursor.execute(insert_sql, (self.cat_name.text(),))
            database.conn.commit()
        except Exception as e:
            database.conn.rollback()
            print(f"save_order(): {e}")
        finally:
            database.disconnect_from_db()
