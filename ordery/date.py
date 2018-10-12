##  ASSUME THE ORDERS TABLE IS LOADED WITH ORDERS!!!
import sqlite3;
from ordery.db import get_db
from flask import current_app
import json

def create_date_table():
    ## Connect to the database
    try:
        conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES);            # Get a connection object for the database
        conn.execute('PRAGMA foreign_keys = ON;');  # Turn on foreign key constraints
        csr = conn.cursor();                        # Get a cursor object for the connection
    except Exception as e:
        print("Error connecting to database: ", e);  # Print error message
        sys.exit(); # Fatal Err

    ## Create date table
    v_sql = 'DROP TABLE IF EXISTS dates;'
    csr.execute(v_sql);

    try:
        v_sql = '''CREATE TABLE dates
               (id INTEGER PRIMARY KEY AUTOINCREMENT ,
                date       TEXT UNIQUE  ,
                day        TEXT NOT NULL,
                month      TEXT NOT NULL
               ); '''
        csr.execute(v_sql);
        print("Date table created successfully");
    except Exception as e:
        print("Error creating orders table: ", e);  # Print error message

    ## Insert data
    try:
        csr.execute('BEGIN TRANSACTION');   # Start transaction
        v_sql = '''INSERT INTO dates (date, day, month)
                   SELECT DISTINCT ord_date, strftime('%w',ord_date), strftime('%m',ord_date)
                   FROM orders
                   WHERE ord_date NOT IN (SELECT date FROM dates);'''
        csr.execute(v_sql);
        conn.commit();                      # Commit the insert or update
    except Exception as e:
        print("Error insert of dates", e);  # Print error message
        conn.rollback();                    # Rollback this transaction

    ## Display the count of dates
    sql = 'SELECT count() FROM dates;'
    print("Count of rows in Dates: ", end = "");
    for t_row in csr.execute(sql): print(t_row[0]);

    ## Create an index on the orders table - ord_date for join efficiency
    sql = 'CREATE INDEX IF NOT EXISTS order_ord_date_idx on orders (ord_date);'
    csr.execute(sql);

    conn.close();

def create_view():
    db = get_db()
    db.executescript('''
    DROP VIEW IF EXISTS v_ord;
    CREATE VIEW IF NOT EXISTS v_ord AS
    SELECT sum(O.ord_qty),
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
          INNER JOIN dates  D ON O.ord_date = D.date
    WHERE date BETWEEN datetime('now', '-380 days') AND datetime('now', 'localtime')
       GROUP BY date;       ''')
    db.commit()



def get_weekly_data(rows):
    labels = {'SUNDAY': 0, 'MONDAY': 0, 'TUESDAY': 0,'WEDNESDAY': 0, 'THURSDAY': 0,'FRIDAY': 0,'SATURDAY': 0}
    d_dict = {};            # Initialize an empty dictionary
    for i in rows: d_dict[i[1]] = (i[0]); # Create the key i[0] and values list
    print(d_dict);
    z = labels.copy()
    z.update(d_dict) #Combine lables and d_dict together
    data = list(z.values())
    return data
