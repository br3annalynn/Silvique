from xlrd import open_workbook, cellname
import model
from flask import Flask, render_template, request, redirect, session, url_for, flash
import datetime
from xlwt import Workbook
import json

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

@app.route("/get_lists")
def get_lists():
    inventory_list = []
    sales_list = []
    rows = model.list_tables()
    for row in rows:
        first_letter = row[0][0]
        if first_letter == "i" or first_letter == "I":
            # skip the main inventory table
            if row[0] != "inventory":
                inventory_list.append(row[0])
        elif first_letter == "s" or first_letter == "S":
            sales_list.append(row[0])
    return json.dumps({'inventory_list' : inventory_list, 'sales_list': sales_list})


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
        sheet = book.sheet_by_index(1)
        # I for inventory, C for comparison, S for sale
        file_type = 'I'
        read_bar_codes(file_name, file_type, sheet)
        return redirect(url_for('display_inventory'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_inventory'))
    

def read_bar_codes(file_name, file_type, sheet):
    if file_type == "S":
        start = 6
    elif file_type == "I":
        start = 5
    else:
        start = 3
    for row_index in range(start, sheet.nrows):
        bar_code = sheet.cell(row_index,0).value
        amount = find_amount(file_type, sheet, row_index)
        # check that cell is not empty
        if bar_code:
            bar_code = bar_code.upper()
            # change last three elements of string to integer
            try:
                value = convert_to_int(sheet.cell(row_index,0).value[-3], sheet.cell(row_index,0).value[-2], sheet.cell(row_index,0).value[-1])
            except TypeError:
                flash(bar_code)
                print "Not a valid sku. Skipping ", bar_code
                continue
            # check that sku is valid (ends in 3 numbers)
            if not value:
                flash(bar_code)
                print "Not a valid sku. Skipping ", bar_code
                continue
            model.check_inventory(file_type, bar_code, value, amount)
            model.add_to_table(file_type, file_name, bar_code, value, amount)
        else:
            continue

def find_amount(file_type, sheet, row_index):
    if file_type == "S":
        amount = -1
    else:
        ################ check where this amount is. Add to template.
        amount = sheet.cell(row_index, 1).value
    # set default value of 1
    # if not amount:
    #     amount = 1
    return amount


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
        read_bar_codes(file_name, file_type, sheet)
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
        read_bar_codes(file_name, file_type, sheet)
        return redirect(url_for('display_inventory'))
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_sale'))

@app.route("/save_inventory")
def save_inv():
    return render_template('save_inventory.html')

@app.route("/save_inventory", methods=['POST'])
def save_inventory():
    current_date = datetime.date.today().strftime("%m/%d/%y")
    global XLS_FOLDER
    book = Workbook()
    sheet1 = book.add_sheet('inventory')
    file_name = request.form.get('file')
    inventory_list = model.show_inventory()
    sheet1.write(0, 0, "Inventory " + current_date) 
    sheet1.write(1, 0, "Tag Total")
    sheet1.write(2, 0, "1/2 Tag Total")
    sheet1.write(4, 0, "Sku")
    sheet1.write(4, 1, "#")
    sheet1.write(4, 2, "Tag")
    sheet1.write(4, 3, "Total")

    total = 0
    single_row = 0
    while single_row < len(inventory_list):
        print_row = sheet1.row(single_row + 5)
        for i in range(0, 4):
            print_row.write(i, inventory_list[single_row][i])
        total += inventory_list[single_row][3]
        single_row +=1

    sheet1.write(1, 1, total)
    sheet1.write(2, 1, total / 2)
    book.save(XLS_FOLDER + file_name)

    flash("Successfully saved " + file_name)
    return redirect(url_for('save_inv'))

@app.route("/add_skus")
def add_skus():
    return render_template('add_skus.html')

@app.route("/add_skus", methods=['POST'])
# ############### This needs help. Need to be able to specify which table the sku is being added to
def add_new_skus():
    if request.form['btn'] == 'Add to Inventory':
        bar_code = request.form.get('i_sku')
        value = int(request.form.get('i_value'))
        amount = int(request.form.get('i_amount'))
        # file_name = request.form.get('i_file_name')
    else:
        bar_code = request.form.get('s_sku')
        value = int(request.form.get('s_value'))
        amount = -1 * int(request.form.get('s_amount'))
        # file_name = request.form.get('s_file_name')
    file_type = "I"
    model.check_inventory(file_type, bar_code, value, amount)
    # model.add_to_table(file_type, file_name, bar_code, value, amount)
    flash("Successfully added " + bar_code)
    return redirect(url_for('add_skus'))


if __name__ == "__main__":
    app.run(debug=True)



















