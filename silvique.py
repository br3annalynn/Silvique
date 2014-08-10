from xlrd import open_workbook, cellname
import model2
from flask import Flask, render_template, request, redirect, session, url_for, flash
import datetime
from xlwt import Workbook
import json
import config

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"
app.config.from_object(config)

@app.route("/")
def index():
    session_user_id = session.get('session_user_id')    
    return render_template('main.html', session_user_id=session_user_id)

@app.route("/", methods=['POST'])
def login():
    submitted_name = request.form.get('name')
    submitted_password = request.form.get('password')

    user_id = model2.login(submitted_name, submitted_password)
    if user_id:
        session['session_user_id'] = user_id
        folder = model2.get_folder(user_id) 
        session['session_folder'] = folder
        print "Successfully loged in"
        return redirect(url_for("display_inventory"))
    else:
        flash("Username or password incorect.")
        return redirect(url_for("process_login"))

@app.route("/show")
def display_inventory():
    session_user_id = session.get('session_user_id')
    if session_user_id:
        packing_lists = model2.get_packing_lists()
        sales_lists = model2.get_sales_lists()
        inventory_list = model2.show_inventory()
        total = 0
        for row in inventory_list:
            total += row[2] * row[1]
        return render_template('show_inventory.html', inventory_list=inventory_list, total=total, packing_lists=packing_lists, sales_lists=sales_lists, name_of_showing="Current Inventory")
    return redirect(url_for('index'))

@app.route("/show_packing_list/<list_id>")
def show_packing_list(list_id):
    packing_list = model2.get_packing_list_by_id(list_id)
    name = model2.get_packing_list_name_by_id(list_id)[0]
    packing_lists = model2.get_packing_lists()
    sales_lists = model2.get_sales_lists()
    total = 0
    for row in packing_list:
        total += row[2] * row[1]
    return render_template('show_inventory.html', inventory_list=packing_list, total=total, packing_lists=packing_lists, sales_lists=sales_lists, name_of_showing=name)

@app.route("/show_sale/<list_id>")
def show_sale(list_id):
    sale_list = model2.get_sale_by_id(list_id)
    name = model2.get_sale_name_by_id(list_id)[0]
    packing_lists = model2.get_packing_lists()
    sales_lists = model2.get_sales_lists()
    total = 0
    for row in sale_list:
        total += row[2] * row[1]
    return render_template('show_inventory.html', inventory_list=sale_list, total=total, packing_lists=packing_lists, sales_lists=sales_lists, name_of_showing=name)

@app.route("/sku_search", methods=["POST"])
def view_sku():
    sku = request.form.get('sku')
    rows = model2.search_by_sku(sku)
    packing_lists = model2.get_packing_lists()
    sales_lists = model2.get_sales_lists()
    total = 0
    return render_template('show_inventory.html', inventory_list=rows, total=total, packing_lists=packing_lists, sales_lists=sales_lists, name_of_showing=sku)

@app.route("/upload_inv")
def upload_inv():
    session_user_id = session.get('session_user_id')
    if session_user_id:
        return render_template('upload.html')
    return redirect(url_for('index'))

@app.route("/upload_inv", methods=["POST"])
def upload_inventory():
    file_name = request.form.get('file')
    name = request.form.get('name')
    try:
        date = datetime.datetime.strptime(request.form.get('date'), '%m/%d/%Y')
    except ValueError:
        flash("Enter four digit year")
        return redirect(url_for('upload_inventory'))
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(file_name)
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_inventory'))
    sheet = book.sheet_by_index(0)
    sale_id = 0
    pl_id = model2.add_packing_list(name, date)
    read_bar_codes(pl_id, sale_id, sheet)
    return redirect(url_for('display_inventory'))

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/settings", methods=["POST"])
def save_settings():
    session_user_id = session.get('session_user_id')    
    folder = request.form.get('folder')
    success = model2.set_folder(folder, session_user_id)
    return redirect('settings')

def read_bar_codes(pl_id, sale_id, sheet):
    if sale_id:
        start = 6
    else:
        start = 5
    for row_index in range(start, sheet.nrows):
        bar_code = sheet.cell(row_index,0).value
        amount = find_amount(pl_id, sale_id, sheet, row_index)
        # check that cell is not empty
        if bar_code:
            bar_code = bar_code.upper()
            # check that sku is valid (ends in 3 numbers)
            try:
                # change last three elements of string to integer
                value = convert_to_int(sheet.cell(row_index,0).value[-3], sheet.cell(row_index,0).value[-2], sheet.cell(row_index,0).value[-1])
            except TypeError:
                flash(bar_code)
                print "Not a valid sku. Skipping ", bar_code
                continue
            if not value:
                flash(bar_code)
                print "Not a valid sku. Skipping ", bar_code
                continue
            model2.add_item(pl_id, sale_id, bar_code, value, amount)
            # model.check_inventory(file_type, bar_code, value, amount)
        else:
            continue

def find_amount(pl_id, sale_id, sheet, row_index):
    if sale_id:
        amount = -1
    else:
        ################ check where this amount is. Add to template.
        amount = sheet.cell(row_index, 2).value
    # set default value of 1
    if not amount:
        amount = 1
    return amount


def convert_to_int(a, b, c):
    #check if each is a number
    if ord(a) < 48 or 57 < ord(a) or ord(b) < 48 or 57 < ord(b) or ord(c) < 48 or 57 < ord(c):
        print ord(a), ord(b), ord(c)
        return False
    number = (ord(a) - 48) * 100 + (ord(b) - 48) * 10 + (ord(c) - 48)
    return number

@app.route("/print_view")
def print_view():
    current_date = datetime.date.today().strftime("%m/%d/%y")
    inventory_list = model2.show_inventory()
    total = 0
    for row in inventory_list:
        total += row[2] * row[1]
    return render_template('print_view.html', inventory_list=inventory_list, total=total, current_date=current_date)

@app.route("/save_inventory")
def save_inv():
    session_user_id = session.get('session_user_id')
    if session_user_id:
        return render_template('save_inventory.html')
    return redirect(url_for('index'))

@app.route("/save_inventory", methods=['POST'])
def save_inventory():
    current_date = datetime.date.today().strftime("%m/%d/%y")
    book = Workbook()
    sheet1 = book.add_sheet('inventory')
    file_name = request.form.get('file')
    folder_name = session.get('session_folder')    
    inventory_list = model2.show_inventory()
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
        for i in range(0, 3):
            print_row.write(i, inventory_list[single_row][i])
        print_row.write(3, inventory_list[single_row][1] * inventory_list[single_row][2])
        total += inventory_list[single_row][1] * inventory_list[single_row][2]
        single_row +=1

    sheet1.write(1, 1, total)
    sheet1.write(2, 1, total / 2)
    book.save(folder_name + file_name)

    flash("Successfully saved " + file_name)
    return redirect(url_for('save_inv'))


@app.route("/upload_sale")
def upload_sale():
    session_user_id = session.get('session_user_id')
    if session_user_id:
        return render_template('upload_sale.html')
    return redirect(url_for('index'))

@app.route("/upload_sale", methods=["POST"])
def upload_sales_report():
    file_name = request.form.get('file')
    location = request.form.get('location')
    try:
        date = datetime.datetime.strptime(request.form.get('date'), '%m/%d/%Y')
    except ValueError:
        flash("Enter four digit year")
        return redirect(url_for('upload_sale'))
    print "******************Trying to open ", file_name
    try:
        book = open_workbook(file_name)
    except IOError:
        flash("File not found. Check file name. ")
        print "No file found with the name ", file_name
        return redirect(url_for('upload_sale'))
    sheet = book.sheet_by_index(0)
    sale_id = model2.add_sale(location, date)
    pl_id = 0
    read_bar_codes(pl_id, sale_id, sheet)
    return redirect(url_for('display_inventory'))
    
@app.route("/add_skus")
def add_skus():
    packing_lists = model2.get_packing_lists()
    sales_lists = model2.get_sales_lists()
    return render_template('add_skus.html', packing_lists=packing_lists, sales_lists=sales_lists)

@app.route("/add_skus", methods=['POST'])
def add_new_skus():
    list_type = request.form.get('list_type')
    pl_id = check_if_none(request.form.get('add-packing-select'))
    sale_id = check_if_none(request.form.get('add-sales-select'))
    bar_code = request.form.get('sku')
    value = int(request.form.get('value'))
    amount = get_amount(list_type, int(request.form.get('amount')))
    print "#########", pl_id, sale_id, bar_code, value, amount
    #model2.add_item(pl_id, sale_id, bar_code, value, amount)
    flash("Successfully added " + bar_code)
    return redirect(url_for('add_skus'))

def check_if_none(list_id):
    print "*************", list_id
    if not list_id:
        return 0
    return list_id

def get_amount(list_type, amount):
    if list_type == "sale":
        amount *= -1
    return amount

def get_ids(selected_list):
    selected_list_array = selected_list.split('-')
    list_type = selected_list_array[0]
    list_id = selected_list_array[1]
    print '!!!!!!!!!', list_type
    if list_type == "p":
        pl_id = list_id
        sale_id = 0
    elif list_type == "s":
        pl_id = 0
        sale_id = list_id
    else:
        return (-1, -1)
    return (pl_id, sale_id)

@app.route("/get_lists")
def get_lists():
    sales_lists = model2.get_sales_lists();
    packing_lists = model2.get_packing_lists();
    return {'sales_lists': sales_lists, 'packing_lists' :packing_lists}

@app.route("/delete_inv")
def delete_inventory():
    model.clear("I")
    return redirect(url_for('display_inventory'))


# @app.route("/display_compare", methods=["POST"])
# def upload_comparison():
#     global XLS_FOLDER
#     file_name = request.form.get('file')
#     print "******************Trying to open ", file_name
#     try:
#         book = open_workbook(XLS_FOLDER + file_name)
#         sheet = book.sheet_by_index(0)
#         # I for inventory, C for comparison, S for sale
#         file_type = 'C'
#         read_bar_codes(file_name, file_type, sheet)
#         return redirect(url_for('display_comparison'))
#     except IOError:
#         flash("File not found. Check file name. ")
#         print "No file found with the name ", file_name
#         return redirect(url_for('upload_comparison'))

# @app.route("/display_compare")
# def display_comparison():
#     (rows, inventory_only_items, comparison_only_items, unequal_items) = model.show_comparison()
#     return render_template('display_compare.html', rows=rows, inventory_only_items=inventory_only_items, comparison_only_items=comparison_only_items, unequal_items=unequal_items)

# @app.route("/print_view_compare")
# def print_view_compare():
#     current_date = datetime.date.today().strftime("%m/%d/%y")
#     (rows, inventory_only_items, comparison_only_items, unequal_items) = model.show_comparison()
#     return render_template('print_view_compare.html', rows=rows, inventory_only_items=inventory_only_items, comparison_only_items=comparison_only_items, unequal_items=unequal_items, current_date=current_date)

# @app.route("/delete_compare")
# def delete_comparison():
#     model.clear('C')
#     return redirect(url_for('display_comparison'))



@app.route("/clear")
def clear():
    session.clear()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)



















