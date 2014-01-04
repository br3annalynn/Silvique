import sqlite3

DB = None
CONN = None

def connect_to_db():
    global DB, CONN
    CONN = sqlite3.connect('inventory.db')
    DB = CONN.cursor()

def check_inventory(bar_code, value):
    connect_to_db()
    query = """SELECT amount, singleValue, totalValue FROM inventory WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    row = DB.fetchone()
    if not row:
        amount = 1
        single_value = value
        total_value = value
    else:
        delete_row(bar_code)
        amount = row[0] + 1
        single_value = row[1]
        total_value = single_value * amount
    add_to_inventory(bar_code, amount, single_value, total_value)

def delete_row(bar_code):
    connect_to_db()
    query = """DELETE FROM inventory WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    CONN.commit()
    print "deleted item", bar_code

def add_to_inventory(bar_code, amount, single_value, total_value):
    connect_to_db()
    query = """INSERT into inventory values (?, ?, ?, ?)"""
    DB.execute(query, (bar_code, amount, single_value, total_value))
    CONN.commit()
    print "Added item", bar_code

def show_inventory():
    connect_to_db()
    query = """SELECT * from inventory ORDER BY barCode"""
    DB.execute(query, ())
    rows = DB.fetchall()
    return rows















