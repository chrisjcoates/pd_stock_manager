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


class EditProduct(QWidget):
    closed_signal = Signal()

    def __init__(self, record_id):
        super().__init__()

        self.setWindowTitle("Edit Product")

        self.record_id = record_id

        self.page_layout = QFormLayout(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.create_widgets()
        self.get_selected_record()

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
        submit_button.clicked.connect(self.update_product)

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

    def get_selected_record(self):

        selected_record = Database().get_stock_data(self.record_id)

        self.name_input.setText(selected_record[0][1])
        self.desc_input.setText(selected_record[0][2])
        self.prod_code_input.setText(selected_record[0][3])
        self.qty_input.setValue(selected_record[0][4])
        self.re_order_input.setValue(selected_record[0][5])
        self.sup_input.setCurrentText(selected_record[0][6])
        self.loc_input.setCurrentText(selected_record[0][7])
        self.bay_input.setCurrentText(selected_record[0][8])
        self.price_input.setValue(float(selected_record[0][9][1::]))

    def update_product(self):
        pass
