from xlrd import open_workbook, cellname
import model
from flask import Flask, render_template, request, redirect, session, url_for, flash
import datetime

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

XLS_FOLDER = 'xls/'

@app.route("/")
def index():
    return render_template('main.html')

@app.route("/show")
def display_inventory():
    inventory_list = model.show_inventory()
    total = 0
    for row in inventory_list:
        total += row[3]
    return render_template('show_inventory.html', inventory_list=inventory_list, total=total)


@app.route("/upload_inv")
def upload_inv():
    return render_template('upload.html')


@app.route("/upload_inv", methods=["POST"])
def upload_inventory():
    global XLS_FOLDER
    file_name = request.form.get('file')
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(XLS_FOLDER + file_name)
        sheet = book.sheet_by_index(0)
        # I for inventory, C for comparison, S for sale
        file_type = 'I'
        read_bar_codes(file_type, sheet)
        return redirect(url_for('display_inventory'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_inventory'))
    

def read_bar_codes(file_type, sheet):
    if file_type == "S":
        start = 6
    elif file_type == "I":
        start = 5
    else:
        # check where Nancy will start comarison files
        start = 0
    for row_index in range(start, sheet.nrows):
        bar_code = sheet.cell(row_index,0).value
        # check that cell is not empty
        if bar_code:
            # change last three elements of string to integer
            value = convert_to_int(sheet.cell(row_index,0).value[-3], sheet.cell(row_index,0).value[-2], sheet.cell(row_index,0).value[-1])
            # check that sku is valid (ends in 3 numbers)
            if not value:
                flash(bar_code)
                print "Not a valid sku. Skipping ", bar_code
                continue
            if file_type == "S":
                model.delete_from_inventory(bar_code, value)
            else:
                model.check_inventory(file_type, bar_code, value)
        else:
            continue

def convert_to_int(a, b, c):
    #check if each is a number
    if ord(a) < 48 or 57 < ord(a) or ord(b) < 48 or 57 < ord(b) or ord(c) < 48 or 57 < ord(c):
        print ord(a), ord(b), ord(c)
        return False
    number = 0
    number += (ord(a) - 48) * 100 + (ord(b) - 48) * 10 + (ord(c) - 48)
    return number

@app.route("/print_view")
def print_view():
    current_date = datetime.date.today().strftime("%m/%d/%y")
    inventory_list = model.show_inventory()
    total = 0
    for row in inventory_list:
        total += row[3]
    return render_template('print_view.html', inventory_list=inventory_list, total=total, current_date=current_date)

@app.route("/delete_inv")
def delete_inventory():
    model.clear("I")
    return redirect(url_for('display_inventory'))


@app.route("/display_compare", methods=["POST"])
def upload_comparison():
    global XLS_FOLDER
    file_name = request.form.get('file')
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(XLS_FOLDER + file_name)
        sheet = book.sheet_by_index(0)
        # I for inventory, C for comparison, S for sale
        file_type = 'C'
        read_bar_codes(file_type, sheet)
        return redirect(url_for('display_comparison'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_comparison'))

@app.route("/display_compare")
def display_comparison():
    (rows, inventory_only_items, comparison_only_items, unequal_items) = model.show_comparison()
    return render_template('display_compare.html', rows=rows, inventory_only_items=inventory_only_items, comparison_only_items=comparison_only_items, unequal_items=unequal_items)

@app.route("/print_view_compare")
def print_view_compare():
    current_date = datetime.date.today().strftime("%m/%d/%y")
    (rows, inventory_only_items, comparison_only_items, unequal_items) = model.show_comparison()
    return render_template('print_view_compare.html', rows=rows, inventory_only_items=inventory_only_items, comparison_only_items=comparison_only_items, unequal_items=unequal_items, current_date=current_date)

@app.route("/delete_compare")
def delete_comparison():
    model.clear('C')
    return redirect(url_for('display_comparison'))


@app.route("/upload_sale")
def upload_sale():
    return render_template('upload_sale.html')

@app.route("/upload_sale", methods=["POST"])
def upload_sales_report():
    global XLS_FOLDER
    file_name = request.form.get('file')
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(XLS_FOLDER + file_name)
        sheet = book.sheet_by_index(0)
        # I for inventory, C for comparison, S for sale
        file_type = 'S'
        read_bar_codes(file_type, sheet)
        return redirect(url_for('display_inventory'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_sale'))


if __name__ == "__main__":
    app.run(debug=True)
