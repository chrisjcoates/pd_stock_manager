from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QToolBar,
)
from PySide6.QtCore import Qt
from pages.home import Home
from pages.stock_table import StockTable
from pages.options import OptionsWindow
from pages.orders_table import OrdersTable
from pages.purchase_orders_table import PurchaseOrdersTable
from pages.customers_table import CustomerTable
from pages.supplier_table import SupplierTable
from pages.locations_table import LocationsTable
from pages.lock_sets_table import LockSetsTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Management System")
        self.resize(1300, 600)

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Records last page
        self.last_page = None

        # Create nav bar
        self.nav_bar = QToolBar("Navigation")
        self.addToolBar(Qt.TopToolBarArea, self.nav_bar)
        self.nav_bar.setMovable(False)

        self.home_btn = QPushButton(text="Home")
        self.stock_btn = QPushButton(text="Stock")
        self.orders_btn = QPushButton(text="Picking Lists")
        self.po_btn = QPushButton(text="Purchase Orders")
        self.customer_btn = QPushButton(text="Customers")
        self.supplier_btn = QPushButton(text="Suppliers")
        self.locations_btn = QPushButton(text="Locations")
        self.locksets_btn = QPushButton(text="Lock Sets")
        self.reports_btn = QPushButton(text="Reports")
        self.options_btn = QPushButton(text="Options")

        # Create button click events
        self.home_btn.clicked.connect(lambda: self.switch_page(0, "home"))
        self.stock_btn.clicked.connect(lambda: self.switch_page(1, "stock"))
        self.orders_btn.clicked.connect(lambda: self.switch_page(2, "orders"))
        self.po_btn.clicked.connect(lambda: self.switch_page(3, "po"))
        self.customer_btn.clicked.connect(lambda: self.switch_page(4, "customer"))
        self.supplier_btn.clicked.connect(lambda: self.switch_page(5, "supplier"))
        self.locations_btn.clicked.connect(lambda: self.switch_page(6, "locations"))
        self.locksets_btn.clicked.connect(lambda: self.switch_page(7, "lock_sets"))
        self.options_btn.clicked.connect(lambda: self.switch_page(8, "options"))

        self.nav_bar.addWidget(self.home_btn)
        self.nav_bar.addWidget(self.stock_btn)
        self.nav_bar.addWidget(self.orders_btn)
        self.nav_bar.addWidget(self.po_btn)
        self.nav_bar.addWidget(self.customer_btn)
        self.nav_bar.addWidget(self.supplier_btn)
        self.nav_bar.addWidget(self.locations_btn)
        self.nav_bar.addWidget(self.locksets_btn)
        self.nav_bar.addWidget(self.reports_btn)
        self.nav_bar.addWidget(self.options_btn)

        # Stacked widgets for pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

    def switch_page(self, index, page):
        """
        Switches the page based on Navigation button selection.
        Also check for methods and calls them.
        """
        if self.pages.currentWidget():
            self.pages.removeWidget(self.pages.currentWidget())

        match page:
            case "home":
                pass
            case "stock":
                self.pages.addWidget(StockTable())
            case "orders":
                self.pages.addWidget(OrdersTable())
            case "options":
                self.pages.addWidget(OptionsWindow())
            case "po":
                self.pages.addWidget(PurchaseOrdersTable())
            case "customer":
                self.pages.addWidget(CustomerTable())
            case "supplier":
                self.pages.addWidget(SupplierTable())
            case "locations":
                self.pages.addWidget(LocationsTable())
            case "lock_sets":
                self.pages.addWidget(LockSetsTable())

        # Set page to the index passed into method
        self.pages.setCurrentIndex(index)
        current_page = self.pages.currentWidget()
        self.last_page = self.pages.currentWidget()

        # checks if the page had specified methods
        if hasattr(current_page, "refresh_table"):
            current_page.refresh_table()
        if hasattr(current_page, "read_database_settings"):
            current_page.read_database_settings()
