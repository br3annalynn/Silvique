import sqlite3

DB = None
CONN = None

def connect_to_db():
    global DB, CONN
    CONN = sqlite3.connect('inventory.db')
    DB = CONN.cursor()

def check_inventory(file_type, bar_code, value, number):
    connect_to_db()
    if file_type == "C":
        query = """SELECT amount, singleValue, totalValue FROM comparison WHERE barCode = ?"""
    else:
        query = """SELECT amount, singleValue, totalValue FROM inventory WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    row = DB.fetchone()
    if not row:
        amount = number
        single_value = value
        total_value = single_value * amount
    else:
        delete_row(file_type, bar_code)
        amount = row[0] + number
        single_value = row[1]
        total_value = single_value * amount
    add_to_inventory(file_type, bar_code, amount, single_value, total_value)

def delete_row(file_type, bar_code):
    connect_to_db()
    if file_type == "C":
        query = """DELETE FROM comparison WHERE barCode = ?"""
    else:
        query = """DELETE FROM inventory WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    CONN.commit()
    # print "deleted item", bar_code

def add_to_inventory(file_type, bar_code, amount, single_value, total_value):
    connect_to_db()
    if file_type == "C":
        query = """INSERT into comparison values (?, ?, ?, ?)"""
    else:
        query = """INSERT into inventory values (?, ?, ?, ?)"""
    DB.execute(query, (bar_code, amount, single_value, total_value))
    CONN.commit()
    # print "Added item", bar_code

def add_to_table(file_type, file_name, bar_code, value, number):
    # see if table exists
    file_name = file_name[:-4]
    connect_to_db()
    query = """CREATE TABLE IF NOT EXISTS """ + file_name + """ (barCode varchar(30), amount int, singleValue int, totalValue int)"""
    DB.execute(query, ())
    CONN.commit()
    query = """SELECT amount, singleValue, totalValue FROM """ + file_name + """ WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    row = DB.fetchone()
    if not row:
        amount = number
        single_value = value
        total_value = single_value * amount
    else:
        delete_row_from_table(file_name, bar_code)
        amount = row[0] + number
        single_value = row[1]
        total_value = single_value * amount
    query = """INSERT into """ + file_name + """ values (?, ?, ?, ?)"""
    DB.execute(query, (bar_code, amount, value, total_value))
    CONN.commit() 

def delete_row_from_table(file_name, bar_code):
    connect_to_db()
    query = """DELETE FROM """ + file_name + """ WHERE barCode = ?"""
    DB.execute(query, (bar_code,))
    CONN.commit()

def show_inventory():
    connect_to_db()
    query = """SELECT * from inventory WHERE amount > 0 ORDER BY barCode COLLATE NOCASE"""
    DB.execute(query, ())
    rows = DB.fetchall()
    return rows

def clear(file_type):
    connect_to_db()
    if file_type == "I":
        query = """DELETE from inventory"""
    else:
        query = """DELETE from comparison"""
    DB.execute(query, ())
    CONN.commit()
    print "All rows deleted"


def show_comparison():
    connect_to_db()
    # check if there is a comparison file uploaded
    query = """SELECT * from comparison"""
    DB.execute(query, ())
    rows = DB.fetchall()

    # find items only in inventory
    query = """SELECT barCode from inventory where amount > 0 and barCode not in (select barCode from comparison where amount > 0) ORDER BY barCode COLLATE NOCASE"""
    DB.execute(query, ())
    inventory_only_bar_codes = DB.fetchall()
    inventory_only_items = []
    for code in inventory_only_bar_codes:
        query = """SELECT * from inventory where barCode = ?"""
        DB.execute(query, (code[0],))
        item = DB.fetchone()
        inventory_only_items.append(item)

    #find items only in comparison
    query = """SELECT barCode from comparison where amount > 0 and barCode not in (select barCode from inventory where amount > 0) ORDER BY barCode COLLATE NOCASE"""
    DB.execute(query, ())
    comparison_only_bar_codes = DB.fetchall()
    comparison_only_items = []
    for code in comparison_only_bar_codes:
        query = """SELECT * from comparison where barCode = ?"""
        DB.execute(query, (code[0],))
        item = DB.fetchone()
        comparison_only_items.append(item)

    # find items in both with unequal amounts
    query = """SELECT * from inventory join comparison on inventory.barCode = comparison.barCode where inventory.amount != comparison.amount ORDER BY barCode COLLATE NOCASE"""
    DB.execute(query, ())
    unequal_items = DB.fetchall()

    return (rows, inventory_only_items, comparison_only_items, unequal_items)

def list_tables():
    connect_to_db()
    query = """SELECT name FROM sqlite_master WHERE type='table';"""
    DB.execute(query, ())
    rows = DB.fetchall()
    return rows












