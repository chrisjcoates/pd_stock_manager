import psycopg2
import json
from datetime import datetime


class Database:
    def __init__(self):

        self._db_details = self.get_db_details()

        self.HOST = self._db_details["host"]
        self.PORT = self._db_details["port"]
        self.DB_NAME = self._db_details["db_name"]
        self.USER = self._db_details["user"]
        self.PASSWORD = self._db_details["password"]

        self.conn = None
        self.cursor = None

    def update_db_connection(self):
        self._db_details = self.get_db_details()
        self.HOST = self._db_details["host"]
        self.PORT = self._db_details["port"]
        self.DB_NAME = self._db_details["db_name"]
        self.USER = self._db_details["user"]
        self.PASSWORD = self._db_details["password"]

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

    def get_stock_data(self, id=None):

        if id:
            sql_query = """
            SELECT stock.stockID, product.productName, productDescription, product.productCode, stock.stockQty, stock.reOrderQty, supplier.supplierName, locations.locationName, bays.bayName, CONCAT('£', product.productPrice * stock.stockQty), product.productID
            FROM stock
            INNER JOIN product ON stock.productID = product.productID
            INNER JOIN supplier ON product.supplierID = supplier.supplierID
            INNER JOIN bays ON stock.bayID = bays.bayID
            INNER JOIN locations ON bays.locationID = locations.locationID
            WHERE stock.stockID = %s
            """

            self.connect_to_db()
            data = None
            try:
                self.cursor.execute(sql_query, id)
                data = self.cursor.fetchall()
            except Exception as e:
                print(f"Error retrieving data from table, {e}")
            self.disconnect_from_db()

            if data:
                return data
        else:
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

    def update_product(
        self, stock_id, prod_id, name, desc, code, price, sup_id, bay_id, qty, reorder
    ):
        # Connect to db
        self.connect_to_db()
        # Get current time stamp
        time_stamp = datetime.now()
        # product table sql
        sql_product = """
        UPDATE product
        SET productName = %(name)s,
            productDescription = %(desc)s,
            productCode = %(code)s,
            productPrice = %(price)s,
            supplierID = %(sup_id)s,
            productDateUpdated = %(time_stamp)s
        WHERE productID = %(prod_id)s
        """
        # Execute sql statement
        try:
            self.cursor.execute(
                sql_product,
                {
                    "name": name,
                    "desc": desc,
                    "code": code,
                    "price": price,
                    "sup_id": sup_id,
                    "time_stamp": time_stamp,
                    "prod_id": prod_id,
                },
            )
            self.conn.commit()
        except Exception as e:
            print(e)
        # Stock table sql
        sql_stock = """
        UPDATE stock
        SET productID = %(prod_id)s,
            bayID = %(bay_id)s,
            stockQty = %(qty)s,
            reorderQTY = %(reorder)s
        WHERE stockID = %(stock_id)s
        """
        # Execute sql statement
        try:
            self.cursor.execute(
                sql_stock,
                {
                    "prod_id": prod_id,
                    "bay_id": bay_id,
                    "qty": qty,
                    "reorder": reorder,
                    "stock_id": stock_id,
                },
            )
            self.conn.commit()
        except Exception as e:
            print(e)
        # Disconnect from db
        self.disconnect_from_db()

    def get_locations(self):

        data = None

        self.connect_to_db()

        sql_query = """
        SELECT * FROM locations;
        """
        try:
            self.cursor.execute(sql_query)

            data = self.cursor.fetchall()
        except Exception as e:
            print(e)

        self.disconnect_from_db()

        return data

    def get_suppliers(self):
        data = None

        self.connect_to_db()

        sql_query = """
        SELECT * FROM supplier;
        """

        try:
            self.cursor.execute(sql_query)

            data = self.cursor.fetchall()
        except Exception as e:
            print(e)

        self.disconnect_from_db()

        return data

    def get_bays(self):
        data = None

        self.connect_to_db()

        sql_query = """
        SELECT * FROM bays;
        """

        try:
            self.cursor.execute(sql_query)

            data = self.cursor.fetchall()
        except Exception as e:
            print(e)

        self.disconnect_from_db()

        return data

    def insert_new_product(self, name, desc, code, price, sup_id, bay_id, qty, reorder):

        self.connect_to_db()

        sql_product = """
        INSERT INTO product (productName, productDescription, productCode, productPrice, supplierID)
        VALUES (%(name)s, %(desc)s, %(code)s, %(price)s, %(sup_id)s)
        RETURNING productID;
        """

        sql_stock = """
        INSERT INTO stock (productID, bayID, stockQty, reorderQty)
        VALUES (%(prod_id)s, %(bay_id)s, %(qty)s, %(reorder)s);
        """

        try:
            print("trying first statement")
            self.cursor.execute(
                sql_product,
                {
                    "name": name,
                    "desc": desc,
                    "code": code,
                    "price": price,
                    "sup_id": sup_id,
                },
            )
            print("first statement complete")
            prod_id = self.cursor.fetchone()
            prod_id = int(prod_id[0])
            print("trying first statement")
            self.cursor.execute(
                sql_stock,
                {"prod_id": prod_id, "bay_id": bay_id, "qty": qty, "reorder": reorder},
            )
            print("first statement complete")
            self.conn.commit()
            print("Insert successful.")

            self.disconnect_from_db()

        except Exception as e:
            print("Insert Failed.")
            self.conn.rollback()
            print(e)
