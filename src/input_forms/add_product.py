from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from database.database import Database


class AddProduct(QWidget):
    closed_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add New Product")

        self.page_layout = QFormLayout(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.create_widgets()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def create_widgets(self):
        """Create the widgets for the input form"""
        self.name_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.prod_code_input = QLineEdit()
        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(0)
        self.qty_input.setMaximum(9999)

        # Create supplier combo box
        self.sup_input = QComboBox()
        # Get suppliers from database
        suppliers = Database().get_suppliers()
        # Only get the first 2 columns (id, name)
        suppliers = [row[0:2] for row in suppliers]
        # Add values to combo box
        for sup_id, sup_name in suppliers:
            self.sup_input.addItem(sup_name, userData=sup_id)

        # Create location combo box
        self.loc_input = QComboBox()
        # Get locations from database
        locations = Database().get_locations()
        # Only get the first 2 columns (id, name)
        locations = [row[0:2] for row in locations]
        # Add values to combobox
        for loc_id, loc_name in locations:
            self.loc_input.addItem(loc_name, userData=loc_id)

        self.loc_input.currentIndexChanged.connect(lambda: self.update_bays_combo())

        # Create bay combo box
        self.bay_input = QComboBox()
        self.update_bays_combo()

        # Create spin boxes
        self.re_order_input = QSpinBox()
        self.re_order_input.setMinimum(0)
        self.re_order_input.setMaximum(9999)
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(9999)
        self.price_input.setSingleStep(0.01)
        self.price_input.setPrefix("£")

        # Create submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.create_product)

        # Add widgets the the grid layout
        self.page_layout.addRow("Product Name: ", self.name_input)
        self.page_layout.addRow("Description: ", self.desc_input)
        self.page_layout.addRow("Product Code: ", self.prod_code_input)
        self.page_layout.addRow("Qty: ", self.qty_input)
        self.page_layout.addRow("Re-Order Qty: ", self.re_order_input)
        self.page_layout.addRow("Supplier: ", self.sup_input)
        self.page_layout.addRow("Location: ", self.loc_input)
        self.page_layout.addRow("Bay: ", self.bay_input)
        self.page_layout.addRow("Price: ", self.price_input)
        self.page_layout.addRow(submit_button)

    def update_bays_combo(self):
        """update the bays combo box values based on the selection of the location combo box value"""
        self.bay_input.clear()

        # get the bays from the database
        bays = Database().get_bays()
        # Get location id from the location combo box
        loc_id = int(self.loc_input.currentData())
        # filter the bays by the location id
        bays = [row for row in bays if row[3] == loc_id]
        # add the filtered bays to the combo box
        for bay_id, bay_name, bay_desc, loc_id in bays:
            self.bay_input.addItem(bay_name, userData=(bay_id, loc_id))

    def create_product(self):
        """
        Create a product and insert the data into the database,
        Creates a record in the product table, and the stock table.
        """
        # Get the values from the input forms controls
        name = self.name_input.text()
        desc = self.desc_input.text()
        code = self.prod_code_input.text()
        qty = int(self.qty_input.value())
        reorder = int(self.re_order_input.value())
        sup_id = int(self.sup_input.currentData())
        bay_id = int(self.bay_input.currentData()[0])
        price = float(self.price_input.value())

        try:
            # Insert the records into the database
            Database().insert_new_product(
                name=name,
                desc=desc,
                code=code,
                price=price,
                sup_id=sup_id,
                bay_id=bay_id,
                qty=qty,
                reorder=reorder,
            )

            # Create message box to tell used record was saved
            msg = QMessageBox(self)
            msg.setText("Product record has been created.")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except Exception as e:
            print(e)
            msg = QMessageBox(self)
            msg.setText(f"Error creating product record, {e}")
            msg.setWindowTitle("Message")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        # destroy the form object(close)
        self.close()