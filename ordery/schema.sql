DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;

CREATE TABLE products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT ,
                  prod_nbr   TEXT UNIQUE ,
                  prod_line  TEXT NOT NULL,
                  size       TEXT NOT NULL,
                  color      TEXT NOT NULL,
                  price      REAL NOT NULL CHECK(TYPEOF(price) == 'real' AND price > 5.0)
                 );
CREATE TABLE orders
						     (id       INTEGER PRIMARY KEY AUTOINCREMENT,
						               ord_nbr  INTEGER NOT NULL UNIQUE ,
						               ord_date TEXT    NOT NULL,
						               ord_qty  INTEGER NOT NULL CHECK(TYPEOF(ord_qty) == 'integer'),
						               prod_id  INTEGER NOT NULL, FOREIGN KEY(prod_id) REFERENCES products(id) ON DELETE CASCADE
						              );

CREATE TABLE users
                (id      INTEGER PRIMARY KEY AUTOINCREMENT,
                        username  TEXT NOT NULL UNIQUE,
                        password TEXT    NOT NULL
                        );

CREATE INDEX IF NOT EXISTS orders_prod_id_fk on orders (prod_id);

INSERT INTO products(prod_nbr,  prod_line,  size,     color,    price)
						                VALUES  ("tray-01", "tray",     "Large",  "White",  7.50);    -- Good product number
INSERT INTO orders (ord_nbr, ord_date,      ord_qty, prod_id)
						                VALUES  (10,      "2018-10-01", 5,       1);    -- Good orders row
INSERT INTO orders (ord_nbr, ord_date,      ord_qty, prod_id)
						                VALUES  (11,      "2018-10-05", 20,       0);    -- Foreign key constraint
INSERT INTO users (username, password)
                            VALUES  ('admin', 'admin');    -- Foreign key constraint
