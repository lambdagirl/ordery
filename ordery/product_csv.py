import sqlite3;
import csv;
import sys;
from ordery.db import get_db
from flask import current_app
def product_csv(filename):
    ## Connect to the database
    try:
        conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES);            # Get a connection object for the database
        conn.execute('PRAGMA foreign_keys = ON;');  # Turn on foreign key constraints
        csr = conn.cursor();                        # Get a cursor object for the connection
    except Exception as e:
        print("Error connecting to database: ", e);  # Print error message
        sys.exit(); # Fatal Error
## Open the orders csv file
    try:
        f = open(filename, newline='');     # Open the file – default for reading
        r = csv.DictReader(f);                  # Return a dictionary reader iterator for the file
        print("\n csv file openned successfully")
    except Exception as e:
        print("Error opening csv file: ", e);   # Print error message
        sys.exit(); # Fatal Error

    ## --------------------------------------
    ## Loop through the orders csv file and insert each row in the table
    ## File title line: ord_nbr, prod_nbr, ord_qty, ord_date
    for d_row in r: # Loop on each row in the file into a list
        t_row = (d_row['prod_nbr'], d_row['prod_line'], d_row['size'], d_row['color'], float(d_row['price']));

        conn.execute('BEGIN TRANSACTION'); # Start transaction
        try:
            sql = 'SELECT id FROM products WHERE prod_nbr = ?';
            csr.execute(sql,(t_row[0],) );
            t_id = csr.fetchone();  # Get the id in a tuple if exists (only 0 or 1 tuples returned)
            if t_id == None:        # Product number does not exist in products
                v_sql = '''INSERT INTO products (prod_nbr, prod_line, size, color, price)
                                     VALUES (?,?,?,?,?);'''
                conn.execute(v_sql, (t_row));
                sql = 'INSERT INTO products (prod_nbr, price) VALUES (?,?);'
            else:
                sql = 'UPDATE products SET price = ? WHERE id = ?';
                csr.execute(sql, (t_row[4], t_id[0]));
            conn.commit();      # Commit the insert or update
            print("inserted!");   # Print error message

        except Exception as e:
            print("Error insert\\update of product: ", t_row[0], e);  # Print error message
            conn.rollback();   # Rollback this transaction
    f.close();  # Close the file
