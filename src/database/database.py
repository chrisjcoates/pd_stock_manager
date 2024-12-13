import psycopg2
import json


class Database:
    def __init__(self):

        self._db_details = self.get_db_details()

        self.HOST = self._db_details["host"]  # work
        self.PORT = self._db_details["port"]  # work
        self.DB_NAME = self._db_details["db_name"]
        self.USER = self._db_details["user"]
        self.PASSWORD = self._db_details["password"]  # work
        # self.HOST = "localhost"  # home
        # self.PORT = "5433" # home
        # self.USER = "postgres" # home
        # self.PASSWORD = "" # home

        self.conn = None
        self.cursor = None

    def update_db_connection(self):
        self._db_details = self.get_db_details()
        self.HOST = self._db_details["host"]  # work
        self.PORT = self._db_details["port"]  # work
        self.DB_NAME = self._db_details["db_name"]
        self.USER = self._db_details["user"]
        self.PASSWORD = self._db_details["password"]  # work

    def get_db_details(self):
        data = False
        try:
            with open("src/settings/settings.json", "r") as file:
                data = json.load(file)
        except Exception as e:
            print(e)

        if data:
            return data["database"]

    def check_db_connection(self):
        try:
            self.conn = psycopg2.connect(
                host=self.HOST,
                port=self.PORT,
                dbname=self.DB_NAME,
                user=self.USER,
                password=self.PASSWORD,
                connect_timeout=5,
            )
            return True
        except Exception as e:
            return False

    def connect_to_db(self):
        try:
            print("attempting database connection...")
            self.conn = psycopg2.connect(
                host=self.HOST,
                port=self.PORT,
                dbname=self.DB_NAME,
                user=self.USER,
                password=self.PASSWORD,
                connect_timeout=5,
            )
            print("connecting...")

            self.cursor = self.conn.cursor()
            print(f"Connected to database '{self.DB_NAME}'")
        except Exception as e:
            print(f"Error connecting to database '{self.DB_NAME}', '{e}'")

    def disconnect_from_db(self):
        try:
            self.cursor.close()
            self.conn.close()
            print(f"Disconnected from database {self.DB_NAME}")
        except Exception as e:
            print(e)

    def get_stock_data(self):

        sql_query = """
        SELECT stock.stockID, product.productName, productDescription, product.productCode, stock.stockQty, stock.reOrderQty, supplier.supplierName, locations.locationName, bays.bayName, CONCAT('£', product.productPrice * stock.stockQty)
        FROM stock
        INNER JOIN product ON stock.productID = product.productID
        INNER JOIN supplier ON product.supplierID = supplier.supplierID
        INNER JOIN bays ON stock.bayID = bays.bayID
        INNER JOIN locations ON bays.locationID = locations.locationID
        ORDER BY stock.stockID;
        """

        self.connect_to_db()
        data = None
        try:
            self.cursor.execute(sql_query)
            data = self.cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving data from table, {e}")
        self.disconnect_from_db()

        if data:
            return data

    def get_locations(self):

        self.connect_to_db()

        sql_query = """
        SELECT * FROM locations;
        """
        try:
            self.cursor.execute(sql_query)

            data = self.cursor.fetchall()
        except Exception as e:
            print(e)

        return data
