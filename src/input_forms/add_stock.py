from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
)
from PySide6.QtCore import Qt
from database.database import Database


class AddStock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Stock Item")

        self.page_layout = QFormLayout(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.create_widgets()

    def create_widgets(self):
        name_input = QLineEdit()
        desc_input = QLineEdit()
        prod_code_input = QLineEdit()
        qty_input = QSpinBox()
        qty_input.setMinimum(0)
        qty_input.setMaximum(9999)

        # Create supplier combo box
        sup_input = QComboBox()

        # Create location combo box
        self.loc_input = QComboBox()
        # Get locations from database
        locations = Database().get_locations()
        # Only get the first 2 columns (id, name)
        locations = [row[0:2] for row in locations]
        # Add values to combobox
        for loc_id, loc_name in locations:
            self.loc_input.addItem(loc_name, userData=loc_id)

        # Create bay cobo box
        bay_input = QComboBox()

        # Create spin boxes
        re_order_input = QSpinBox()
        re_order_input.setMinimum(0)
        re_order_input.setMaximum(9999)
        price_input = QDoubleSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(9999)
        price_input.setSingleStep(0.01)
        price_input.setPrefix("£")

        submit_button = QPushButton("Submit")

        self.page_layout.addRow("Item Name: ", name_input)
        self.page_layout.addRow("Description: ", desc_input)
        self.page_layout.addRow("Product Code: ", prod_code_input)
        self.page_layout.addRow("Qty: ", qty_input)
        self.page_layout.addRow("Re-Order Qty: ", re_order_input)
        self.page_layout.addRow("Supplier: ", sup_input)
        self.page_layout.addRow("Location: ", self.loc_input)
        self.page_layout.addRow("Bay: ", bay_input)
        self.page_layout.addRow("Price: ", price_input)
        self.page_layout.addRow(submit_button)
