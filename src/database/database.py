import psycopg2
import json
from datetime import datetime
from classes.functions import read_settings_json


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
        if self._db_details:
            self.HOST = self._db_details["host"]
            self.PORT = self._db_details["port"]
            self.DB_NAME = self._db_details["db_name"]
            self.USER = self._db_details["user"]
            self.PASSWORD = self._db_details["password"]

    def get_db_details(self):

        data = read_settings_json()

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
            # print("attempting database connection...")
            self.conn = psycopg2.connect(
                host=self.HOST,
                port=self.PORT,
                dbname=self.DB_NAME,
                user=self.USER,
                password=self.PASSWORD,
                connect_timeout=5,
            )
            # print("connecting...")

            self.cursor = self.conn.cursor()
            # print(f"Connected to database '{self.DB_NAME}'")
        except Exception as e:
            print(f"Error connecting to database '{self.DB_NAME}', '{e}'")

    def disconnect_from_db(self):
        try:
            self.cursor.close()
            self.conn.close()
            # print(f"Disconnected from database {self.DB_NAME}")
        except Exception as e:
            print(e)

    def get_stock_data(self, id=None, active=True):

        if id:
            sql_query = """
            SELECT stock.stockID, product.productName, productDescription, product.productCode, stock.stockQty, stock.reOrderQty, supplier.supplierName, locations.locationName, bays.bayName, product.productPrice, product.productID, TO_CHAR(stock.stockDateUpdated, 'DD/MM/YYYY HH:MM:SS'), product_categories.prod_catName, product.status
            FROM stock
            INNER JOIN product ON stock.productID = product.productID
            INNER JOIN supplier ON product.supplierID = supplier.supplierID
            INNER JOIN bays ON stock.bayID = bays.bayID
            INNER JOIN locations ON bays.locationID = locations.locationID
            INNER JOIN product_categories ON product.prod_cat_id = product_categories.prod_cat_id
            WHERE stock.stockID = %(id)s
            """

            self.connect_to_db()
            data = None
            try:
                self.cursor.execute(sql_query, {"id": id})
                data = self.cursor.fetchall()
            except Exception as e:
                print(f"Error retrieving data from table, {e}")
            self.disconnect_from_db()

            if data:
                return data
        else:
            if active:
                sql_query = """
                            SELECT DISTINCT 
                                stock.stockID, 
                                product.productName, 
                                product.productDescription,
                                product_categories.prod_catName, 
                                product.productCode, 
                                supplier.supplierName, 
                                stock.stockQty, 
                                COALESCE(
                                    SUM(
                                        CASE
                                            WHEN order_item.pickingStatus = 'WIP' THEN order_item.orderItemQty
                                            ELSE 0
                                        END
                                    ), 
                                    0
                                ) AS allocatedStock, 
                                (stock.stockQty - COALESCE(
                                    SUM(
                                        CASE
                                            WHEN order_item.pickingStatus = 'WIP' THEN order_item.orderItemQty
                                            ELSE 0
                                        END
                                    ), 
                                    0
                                )) AS stockAvailable,
                                COALESCE(po_line_items_summary.totalOnOrder, 0) AS onOrder,
                                stock.reOrderQty, 
                                locations.locationName, 
                                bays.bayName, 
                                TO_CHAR(product.productPrice * stock.stockQty, 'FM"£"999G999G999G990D00') AS totalStockValue
                            FROM 
                                stock
                            INNER JOIN product ON stock.productID = product.productID
                            INNER JOIN supplier ON product.supplierID = supplier.supplierID
                            INNER JOIN bays ON stock.bayID = bays.bayID
                            INNER JOIN locations ON bays.locationID = locations.locationID
                            INNER JOIN product_categories ON product.prod_cat_id = product_categories.prod_cat_id
                            LEFT JOIN order_item ON order_item.stockID = stock.stockID
                            LEFT JOIN (
                                SELECT stockID, 
                                    SUM(CASE WHEN deliveryStatus = 'WIP' THEN qtyOrdered ELSE 0 END) AS totalOnOrder
                                FROM po_line_items
                                GROUP BY stockID
                            ) AS po_line_items_summary ON po_line_items_summary.stockID = stock.stockID
                            LEFT JOIN orders ON order_item.orderID = orders.orderID
                            WHERE 
                                product.status = 'active'
                            GROUP BY 
                                stock.stockID, 
                                product.productName, 
                                product.productDescription, 
                                product_categories.prod_catName, 
                                product.productCode, 
                                stock.stockQty,
                                stock.reOrderQty, 
                                supplier.supplierName, 
                                locations.locationName, 
                                bays.bayName, 
                                product.productPrice,
                                po_line_items_summary.totalOnOrder
                            ORDER BY 
                                stock.stockID;
                            """
            else:
                sql_query = """
                            SELECT DISTINCT 
                                stock.stockID, 
                                product.productName, 
                                product.productDescription,
                                product_categories.prod_catName, 
                                product.productCode, 
                                supplier.supplierName, 
                                stock.stockQty, 
                                COALESCE(
                                    SUM(
                                        CASE
                                            WHEN order_item.pickingStatus = 'WIP' THEN order_item.orderItemQty
                                            ELSE 0
                                        END
                                    ), 
                                    0
                                ) AS allocatedStock, 
                                (stock.stockQty - COALESCE(
                                    SUM(
                                        CASE
                                            WHEN order_item.pickingStatus = 'WIP' THEN order_item.orderItemQty
                                            ELSE 0
                                        END
                                    ), 
                                    0
                                )) AS stockAvailable,
                                COALESCE(po_line_items_summary.totalOnOrder, 0) AS onOrder,
                                stock.reOrderQty, 
                                locations.locationName, 
                                bays.bayName, 
                                TO_CHAR(product.productPrice * stock.stockQty, 'FM"£"999G999G999G990D00') AS totalStockValue
                            FROM 
                                stock
                            INNER JOIN product ON stock.productID = product.productID
                            INNER JOIN supplier ON product.supplierID = supplier.supplierID
                            INNER JOIN bays ON stock.bayID = bays.bayID
                            INNER JOIN locations ON bays.locationID = locations.locationID
                            INNER JOIN product_categories ON product.prod_cat_id = product_categories.prod_cat_id
                            LEFT JOIN order_item ON order_item.stockID = stock.stockID
                            LEFT JOIN (
                                SELECT stockID, 
                                    SUM(CASE WHEN deliveryStatus = 'WIP' THEN qtyOrdered ELSE 0 END) AS totalOnOrder
                                FROM po_line_items
                                GROUP BY stockID
                            ) AS po_line_items_summary ON po_line_items_summary.stockID = stock.stockID
                            LEFT JOIN orders ON order_item.orderID = orders.orderID
                            WHERE 
                                product.status = 'inactive'
                            GROUP BY 
                                stock.stockID, 
                                product.productName, 
                                product.productDescription, 
                                product_categories.prod_catName, 
                                product.productCode, 
                                stock.stockQty,
                                stock.reOrderQty, 
                                supplier.supplierName, 
                                locations.locationName, 
                                bays.bayName, 
                                product.productPrice,
                                po_line_items_summary.totalOnOrder
                            ORDER BY 
                                stock.stockID;
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
        self,
        stock_id,
        prod_id,
        name,
        desc,
        code,
        prod_cat_id,
        price,
        sup_id,
        bay_id,
        qty,
        reorder,
        status,
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
            prod_cat_id = %(prod_cat_id)s,
            productPrice = %(price)s,
            supplierID = %(sup_id)s,
            productDateUpdated = %(time_stamp)s,
            status = %(status)s
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
                    "prod_cat_id": prod_cat_id,
                    "price": price,
                    "sup_id": sup_id,
                    "time_stamp": time_stamp,
                    "prod_id": prod_id,
                    "status": status,
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
            reorderQTY = %(reorder)s,
            stockDateUpdated = %(time_stamp)s
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
                    "time_stamp": time_stamp,
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

    def get_prod_categories(self):

        data = None

        self.connect_to_db()

        sql_query = """
        SELECT *
        FROM product_categories
        ORDER BY prod_catName ASC;
        """

        try:
            self.cursor.execute(sql_query)

            data = self.cursor.fetchall()
        except Exception as e:
            print(f"get_prod_categories function: {e}")

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

    def insert_new_product(
        self, name, desc, code, price, sup_id, bay_id, qty, reorder, prod_cat_id
    ):

        self.connect_to_db()

        sql_product = """
        INSERT INTO product (productName, productDescription, productCode, productPrice, supplierID, prod_cat_id)
        VALUES (%(name)s, %(desc)s, %(code)s, %(price)s, %(sup_id)s, %(prod_cat_id)s)
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
                    "prod_cat_id": prod_cat_id,
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
            self.disconnect_from_db()

    def get_orders_data(self):

        data = None

        orders_sql = """
                    SELECT orders.orderID, orders.sageNumber, customer.customerName, TO_CHAR(orders.deliveryDate, 'DD/MM/YYYY'), orders.orderStatus, 
                    TO_CHAR(orders.orderDateCreated, 'DD/MM/YYYY'), 
                    TO_CHAR(orders.orderDateUpdated, 'DD/MM/YYYY')
                    FROM orders
                    INNER JOIN customer on customer.customerID = orders.customerID
                    INNER JOIN users on users.userID = orders.userID
                    ORDER BY orders.deliveryDate;
                    """

        self.connect_to_db()

        try:
            self.cursor.execute(orders_sql)
            data = self.cursor.fetchall()
        except Exception as e:
            print(f"get_orders_data function: {e}")

        self.disconnect_from_db()

        return data

    def custom_query(self, query, arg=None):

        data = None

        self.connect_to_db()

        if arg:
            try:
                self.cursor.execute(query, arg)
                data = self.cursor.fetchall()
            except Exception as e:
                print(f"custom_query: {e}")

            self.disconnect_from_db()

            return data
        else:
            try:
                self.cursor.execute(query)
                data = self.cursor.fetchall()
            except Exception as e:
                print(f"custom_query: {e}")

            self.disconnect_from_db()

            return data

    def insert_new_customer(self, name, phone, email):

        self.connect_to_db()

        sql_product = """
        INSERT INTO customer (customerName, customerPhone, customerEmail)
        VALUES (%(name)s, %(phone)s, %(email)s);
        """

        try:
            print("trying first statement")
            self.cursor.execute(
                sql_product,
                {
                    "name": name,
                    "phone": phone,
                    "email": email,
                },
            )
            print("first statement complete")
            self.conn.commit()
            print("Insert successful.")

            self.disconnect_from_db()

        except Exception as e:
            print("Insert Failed.")
            self.conn.rollback()
            print(e)
            self.disconnect_from_db()

    def insert_new_supplier(self, name, first_name, last_name, phone, email):

        self.connect_to_db()

        sql_product = """
        INSERT INTO supplier (supplierName, contactFirstName, contactLastName, supplierPhone, supplierEmail)
        VALUES (%(name)s, %(first_name)s, %(last_name)s, %(phone)s, %(email)s);
        """

        try:
            print("trying first statement")
            self.cursor.execute(
                sql_product,
                {
                    "name": name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "email": email,
                },
            )
            print("first statement complete")
            self.conn.commit()
            print("Insert successful.")

            self.disconnect_from_db()

        except Exception as e:
            print("Insert Failed.")
            self.conn.rollback()
            print(e)
            self.disconnect_from_db()
