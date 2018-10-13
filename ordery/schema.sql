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

  CREATE TABLE dates
                  (id INTEGER PRIMARY KEY AUTOINCREMENT ,
                                    date       TEXT UNIQUE  ,
                                    day        TEXT NOT NULL,
                                    month      TEXT NOT NULL
                                   );

CREATE INDEX IF NOT EXISTS orders_prod_id_fk on orders (prod_id);
--CREATE TRIGGER------------------------------------------------
CREATE VIRTUAL TABLE products_index USING fts5(prod_nbr, prod_line, size, color, price,  content=products, content_rowid=id, tokenize=porter);

-- Trigger on INSERT
CREATE TRIGGER after_products_insert AFTER INSERT ON products BEGIN INSERT INTO products_index ( rowid, prod_nbr, prod_line, size, color, price  ) VALUES(
    new.id,
    new.prod_nbr,
		new.prod_line,
		new.size,
		new.color,
		new.price
  );
END;

-- Trigger on UPDATE
CREATE TRIGGER after_products_update UPDATE OF prod_nbr
	ON products BEGIN
  UPDATE products_index
	SET
	prod_nbr = new.prod_nbr
	WHERE rowid = old.id;
END;

-- Trigger on DELETE
CREATE TRIGGER after_products_delete AFTER DELETE ON products BEGIN
    DELETE FROM products_index WHERE rowid = old.id;
END;

----------------
DROP VIEW IF EXISTS v_ord;
   CREATE VIEW IF NOT EXISTS v_ord AS
   SELECT P.prod_nbr, P.prod_line, P.color, P.size, P.price,
          O.ord_nbr, O.ord_qty,
          P.price * ifnull( O.ord_qty, 0) AS ord_amt,
          D.date, D.month,
          CASE D.day WHEN '0' THEN 'SUNDAY'
                     WHEN '1' THEN 'MONDAY'
                     WHEN '2' THEN 'TUESDAY'
                     WHEN '3' THEN 'WEDNESDAY'
                     WHEN '4' THEN 'THURSDAY'
                     WHEN '5' THEN 'FRIDAY'
                     WHEN '6' THEN 'SATURDAY'
                     ELSE 'OTHER' END AS day_name
    FROM products P
         INNER JOIN orders O ON P.id      = O.prod_id
         INNER JOIN dates  D ON O.ord_ate = D.date;

--INSERT DATA------------------------------------------------
INSERT INTO products(prod_nbr,  prod_line,  size,     color,    price)
						                VALUES  ("tray-01", "tray",     "Large",  "White",  7.50);    -- Good product number
INSERT INTO orders (ord_nbr, ord_date,      ord_qty, prod_id)
						                VALUES  (10,      "2018-10-01", 5,       1);    -- Good orders row
INSERT INTO orders (ord_nbr, ord_date,      ord_qty, prod_id)
						                VALUES  (11,      "2018-10-05", 20,       0);    -- Foreign key constraint
INSERT INTO users (username, password)
                            VALUES  ('admin', 'admin');    -- Foreign key constraint
