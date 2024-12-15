CREATE TABLE supplier (
	supplierID SERIAL,
	supplierName VARCHAR(120) NOT NULL,
	contactFirstName VARCHAR(120),
	contactLastName VARCHAR(120),
	supplierPhone VARCHAR(120),
	supplierEmail VARCHAR(125),
	CONSTRAINT pk_supplier_ID PRIMARY KEY (supplierID)
);
CREATE TABLE product (
	productID SERIAL,
	productNAME VARCHAR(120) NOT NULL,
	productDescription VARCHAR(200),
	productCode VARCHAR(125) NOT NULL,
	productPrice NUMERIC(10,2) DEFAULT 0.00,
	supplierID INT NOT NULL,
	productDateCreated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	productDateUpdated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT pk_productID PRIMARY KEY (productID),
	CONSTRAINT fk_supplierID FOREIGN KEY (supplierID) REFERENCES supplier(supplierID)
);

CREATE TABLE locations (
	locationID SERIAL,
	locationName VARCHAR(120) NOT NULL,
	locationDescription VARCHAR(200),
	locationAddress VARCHAR(200),
	locationCity VARCHAR(100),
	locationPostCode VARCHAR(6),
	CONSTRAINT pk_locationID PRIMARY KEY (locationID)
);

CREATE TABLE bays (
	bayID SERIAL,
	bayNAME VARCHAR(120),
	bayDESCRIPTION VARCHAR(200),
	locationID INT NOT NULL,
	CONSTRAINT pk_bayID PRIMARY KEY (bayID),
	CONSTRAINT fk_locationID FOREIGN KEY (locationID) REFERENCES locations(locationID)
);

CREATE TABLE stock (
	stockID SERIAL,
	productID INT NOT NULL,
	bayID INT NOT NULL,
	stockQty INT DEFAULT 0,
	CONSTRAINT pk_stockID PRIMARY KEY (stockID),
	CONSTRAINT fk_productID FOREIGN KEY (productID) REFERENCES product(productID),
	CONSTRAINT fk_bayID FOREIGN KEY (bayID) REFERENCES bays(bayID)
);

--ALTER TABLE stock
--ADD COLUMN reOrderQty INT DEFAULT 0;

CREATE TABLE customer (
	customerID SERIAL,
	customerName VARCHAR(120) NOT NULL,
	customerPhone VARCHAR(20),
	customerEmail VARCHAR(125),
	CONSTRAINT pk_customerID PRIMARY KEY (customerID)
);

CREATE TABLE users (
	userID SERIAL,
	userFirstName VARCHAR(120) NOT NULL,
	userLastName VARCHAR(120) NOT NULL,
	userName VARCHAR(100) NOT NULL,
	userPassword VARCHAR(255) NOT NULL,
	userEmail VARCHAR(125),
	CONSTRAINT pk_userID PRIMARY KEY (userID)
);

CREATE TABLE orders (
	orderID SERIAL,
	sageNumber INT NOT NULL,
	customerID INT NOT NULL,
	userID INT NOT NULL,
	orderStatus VARCHAR(20),
	orderDateCreated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	orderDateUpdated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT pk_orderID PRIMARY KEY (orderID),
	CONSTRAINT fk_customerID FOREIGN KEY (customerID) REFERENCES customer(customerID),
	CONSTRAINT fk_userID FOREIGN KEY (userID) REFERENCES users(userID)
);

CREATE TABLE order_item (
	orderItemID SERIAL,
	orderID INT NOT NULL,
	stockID INT NOT NULL,
	orderItemQty INT DEFAULT 0,
	pickingStatus VARCHAR(20),
	CONSTRAINT pk_orderItemID PRIMARY KEY (orderItemID),
	CONSTRAINT fk_orderID FOREIGN KEY (orderID) REFERENCES orders(orderID),
	CONSTRAINT fk_stockID FOREIGN KEY (stockID) REFERENCES stock(stockID)
);