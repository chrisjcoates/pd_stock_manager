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
        self.reports_btn = QPushButton(text="Reports")
        self.options_btn = QPushButton(text="Options")

        # Create button click events
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.stock_btn.clicked.connect(lambda: self.switch_page(1, "stock"))
        self.orders_btn.clicked.connect(lambda: self.switch_page(2, "orders"))
        self.options_btn.clicked.connect(lambda: self.switch_page(4))

        self.nav_bar.addWidget(self.home_btn)
        self.nav_bar.addWidget(self.stock_btn)
        self.nav_bar.addWidget(self.orders_btn)
        self.nav_bar.addWidget(self.reports_btn)
        self.nav_bar.addWidget(self.options_btn)

        # Stacked widgets for pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)
        # self.pages.addWidget(Home())
        # self.pages.addWidget(StockTable())
        # self.pages.addWidget(OrdersTable())
        # self.pages.addWidget(Home())
        # self.pages.addWidget(OptionsWindow())

    def switch_page(self, index, page):
        """
        Switches the page based on Navigation button selection.
        Also check for methods and calls them.
        """
        if self.pages.currentWidget():
            self.pages.removeWidget(self.pages.currentWidget())

        match page:
            case "stock":
                self.pages.addWidget(StockTable())
            case "orders":
                self.pages.addWidget(OrdersTable())

        # Set page to the index passed into method
        self.pages.setCurrentIndex(index)
        current_page = self.pages.currentWidget()
        self.last_page = self.pages.currentWidget()

        # checks if the page had specified methods
        if hasattr(current_page, "refresh_table"):
            current_page.refresh_table()
        if hasattr(current_page, "read_database_settings"):
            current_page.read_database_settings()
