from xlrd import open_workbook, cellname
import model
from flask import Flask, render_template, request, redirect, session, url_for, flash

app = Flask(__name__)


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
    ###########change file name to file with inventory
    # book = open_workbook('simple.xls')
    # sheet = book.sheet_by_index(0)
    # read_bar_codes(sheet)
    # return redirect(url_for('display_inventory'))

@app.route("/upload_inv", methods=["POST"])
def upload_inventory():
    file_name = request.form.get('file')
    print "********************opening ", file_name
    book = open_workbook(file_name)
    sheet = book.sheet_by_index(0)
    read_bar_codes(sheet)
    return redirect(url_for('display_inventory'))

def read_bar_codes(sheet):
    # for row_index in range(sheet.nrows):
    for row_index in range(30, 40):
        bar_code = sheet.cell(row_index,0).value
        # change last three elements of string to integer
        value = convert_to_int(sheet.cell(row_index,0).value[-3], sheet.cell(row_index,0).value[-2], sheet.cell(row_index,0).value[-1])
        model.check_inventory(bar_code, value)

def convert_to_int(a, b, c):
    number = 0
    number += (ord(a) - 48) * 100 + (ord(b) - 48) * 10 + (ord(c) - 48)
    return number

@app.route("/print_view")
def print_view():
    inventory_list = model.show_inventory()
    total = 0
    for row in inventory_list:
        total += row[3]
    return render_template('print_view.html', inventory_list=inventory_list, total=total)

    
if __name__ == "__main__":
    app.run(debug=True)
