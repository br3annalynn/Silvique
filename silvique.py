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
        # I for inventory, C for comparison
        file_type = 'I'
        read_bar_codes(file_type, sheet)
        return redirect(url_for('display_inventory'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_inventory'))
    

def read_bar_codes(file_type, sheet):
    for row_index in range(sheet.nrows):
        bar_code = sheet.cell(row_index,0).value
        # change last three elements of string to integer
        value = convert_to_int(sheet.cell(row_index,0).value[-3], sheet.cell(row_index,0).value[-2], sheet.cell(row_index,0).value[-1])
        model.check_inventory(file_type, bar_code, value)

def convert_to_int(a, b, c):
    number = 0
    number += (ord(a) - 48) * 100 + (ord(b) - 48) * 10 + (ord(c) - 48)
    return number

@app.route("/upload_compare")
def upload_compare():
    return render_template('upload_compare.html')

@app.route("/upload_compare", methods=["POST"])
def upload_comparison():
    global XLS_FOLDER
    file_name = request.form.get('file')
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(XLS_FOLDER + file_name)
        sheet = book.sheet_by_index(0)
        # I for inventory, C for comparison
        file_type = 'C'
        read_bar_codes(file_type, sheet)
        return redirect(url_for('display_comparison'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_compare'))

@app.route("/display_compare")
def display_comparison():
    (rows, inventory_only_items, comparison_only_items, unequal_items) = model.show_comparison()
    return render_template('display_compare.html', rows=rows, inventory_only_items=inventory_only_items, comparison_only_items=comparison_only_items, unequal_items=unequal_items)

@app.route("/print_view")
def print_view():
    current_date = datetime.date.today().strftime("%d/%m/%y")
    inventory_list = model.show_inventory()
    total = 0
    for row in inventory_list:
        total += row[3]
    return render_template('print_view.html', inventory_list=inventory_list, total=total, current_date=current_date)

@app.route("/delete_inv")
def delete_inventory():
    model.clear("I")
    return redirect(url_for('display_inventory'))

@app.route("/delete_compare")
def delete_comparison():
    model.clear('C')
    return redirect(url_for('display_comparison'))

if __name__ == "__main__":
    app.run(debug=True)
