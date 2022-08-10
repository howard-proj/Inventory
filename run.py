import database
from flask import Flask, redirect, render_template, flash, url_for, request
import urllib.request
import os
from werkzeug.utils import secure_filename
from datetime import datetime
# from modules import *

user_details = {}
session = {}
page = {}

myDatabase = database.SQLDatabase()
myDatabase.database_setup()


app = Flask(__name__)
app.secret_key = """U29tZWJvZHkgb25jZSB0b2xkIG1lIFRoZSB3b3JsZCBpcyBnb25uYSBy
b2xsIG1lIEkgYWluJ3QgdGhlIHNoYXJwZXN0IHRvb2wgaW4gdGhlIHNoZWQgU2hlIHdhcyBsb29r
aW5nIGtpbmRhIGR1bWIgV2l0aCBoZXIgZmluZ2VyIGFuZCBoZXIgdGh1bWIK"""
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method == 'POST'):
        login_data = myDatabase.check_credentials(
            request.form['username'],
            request.form['password']
        )
        # 1) error case
        if login_data is False:
            page['bar'] = False
            flash("Incorrect username/password, please try again")
            return redirect(url_for('login'))
        
        # 2) no error case
        page['bar'] = True
        flash("You have logged in successfully")
        session['logged_in'] = True

        global user_details
        user_details = login_data[0]

        return redirect(url_for('home'))

    elif(request.method == 'GET'):
        return render_template("login.html", page=page)

@app.route('/home')
def home():
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'User Page'

    user_history = None
    user_history = myDatabase.select_all_history()

    if user_history == None:
        user_history = []

    
    return render_template("home.html", 
                            page=page,
                            session=session,
                            user=user_details,
                            user_history=user_history)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    page['bar'] = True
    flash("You have logged out")
    return redirect(url_for('home'))
    

@app.route('/inventories')
def list_inventories():
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'List Inventories'

    allinventories = None
    allinventories = myDatabase.select_all_inventories()

    # checking for integrity only
    if allinventories == None:
        allinventories = []

    return render_template("listitems/listinventories.html",
                            session=session,
                            page=page,
                            user=user_details,
                            allinventories=allinventories)

@app.route('/inventory/create', methods=["POST", "GET"])
def add_inventory():
    """
    Add a new movie
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Inventory creation'

    # print("request form is:")
    newdict = {}
    # print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('inventoryname' not in request.form):
            newdict['inventoryname'] = 'Empty Inventory Name'
        else:
            newdict['inventoryname'] = request.form['inventoryname']
            # print("We have a value: ",newdict['inventoryname'])
        
        if ('quantity' not in request.form):
            newdict['quantity'] = 'Empty quantity'
        else:
            newdict['quantity'] = request.form['quantity']
            # print("We have a value: ",newdict['quantity'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description/unit field'
        else:
            newdict['description'] = request.form['description']
            # print("We have a value: ",newdict['description'])

        if ('picture' not in request.form):
            newdict['picture'] = 'notfound.png'
        else:
            newdict['picture'] = request.form['picture']

        if request.files['picture'] is None:
            newdict['picture'] = 'notfound.png'
        else:
            file = request.files['picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                newdict['picture'] = file.filename
            else:
                newdict['picture'] = 'notfound.png'

        #forward to the database to manage insert
        myDatabase.add_inventory(newdict['inventoryname'],newdict['quantity'],newdict['description'],newdict['picture'])

        page['bar'] = True
        flash("Added Item Successfully")

        # ideally this would redirect to your newly added movie
        return redirect(url_for('list_inventories'))
    else:
        return render_template('createitems/createinventory.html',
                           session=session,
                           page=page,
                           user=user_details)

                        
@app.route('/inventory/<inventory_id>')
def single_inventory(inventory_id):
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('/login'))

    page['title'] = 'Inventory'

    inventory = None
    inventory = myDatabase.select_inventory(inventory_id)

    if inventory == None:
        inventory = []

    print(inventory)
    return render_template('singleitems/inventory.html',
                            session=session,
                            page=page,
                            user=user_details,
                            inventory=inventory)

@app.route('/inventory/<inventory_id>/edit', methods=['POST', 'GET'])
def edit(inventory_id):
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('/login'))

    # print(user_details)
    # if (user_details['admin'] == 0):
    #     print("ENTERED")
    #     redirect(url_for('list_inventories'))

    page['title'] = 'Inventory edit'

    print("request form is:")
    newdict = {}
    # print(request.form)

     # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('inventoryname' not in request.form):
            newdict['inventoryname'] = 'Empty Inventory Name'
        else:
            newdict['inventoryname'] = request.form['inventoryname']
            # print("We have a value: ",newdict['inventoryname'])
        
        if ('quantity' not in request.form):
            newdict['quantity'] = 'Empty quantity'
        else:
            newdict['quantity'] = request.form['quantity']
            # print("We have a value: ",newdict['quantity'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description/unit field'
        else:
            newdict['description'] = request.form['description']

        # Check if the edit added or subtracted our inventory
        item = myDatabase.select_inventory(inventory_id)
        quantity_before = int(item[0]['quantity'])
        quantity_now = int(newdict['quantity'])

        current_total = quantity_now - quantity_before
        # if there is no change, do nothing
        if (current_total == 0):
            pass
        else:
            # case 1: subtraction of inventory
            time_now = datetime.now()
            if (current_total < 0):
                myDatabase.add_to_history(user_details['user_id'], inventory_id, quantity_before, quantity_now, current_total, time_now.strftime("%d/%m/%Y %H:%M:%S"))

            # case 2: addition of inventory
            elif (current_total > 0):
                myDatabase.add_to_history(user_details['user_id'], inventory_id, quantity_before, quantity_now, current_total, time_now.strftime("%d/%m/%Y %H:%M:%S"))

        #Update the database here
        myDatabase.update_inventory(inventory_id, newdict['inventoryname'], newdict['quantity'], newdict['description'])

        page['bar'] = True
        flash("Updated Successfully")

        return redirect(url_for('list_inventories'))

    else:
        inventory = None
        inventory = myDatabase.select_inventory(inventory_id)

        if inventory == None:
            inventory = []

        return render_template('edit.html',
                                session=session,
                                page=page,
                                user=user_details,
                                inventory=inventory)

@app.route('/inventory/<inventory_id>/remove', methods=['GET', 'POST'])
def remove_inventory(inventory_id):
    if (request.method == 'POST'):
        myDatabase.remove_inventory(inventory_id)

        page['bar'] = True
        flash("Updated Successfully")

        return redirect(url_for('list_inventories'))

    elif (request.method == 'GET'):
        inventory = None
        inventory = myDatabase.select_inventory(inventory_id)

        if inventory == None:
            inventory = []


        return render_template('confirmation/delete.html',
                                session=session,
                                page=page,
                                user=user_details,
                                inventory=inventory)

@app.route('/search/inventories', methods=['GET', 'POST'])
def search_inventories():
     # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'TV Show Search'

    inventories = None
    if (request.method == 'POST'):
        inventories = myDatabase.find_matchinginventories(request.form['searchterm'])

    # data integrity checks
    if inventories == None or inventories == []:
        inventories = []
        page['bar'] = False
        flash("No matching inventories, please try again")
    else:
        page['bar'] = True
        flash('Found ' + str(len(inventories)) + ' inventories')
        session['logged_in'] = True

    return render_template('searchitems/search_inventories.html',
                            session=session,
                            page=page,
                            user=user_details,
                            inventories=inventories)

@app.route('/display/<filename>')
def display_image(filename):
    print("images/" + filename)
    return redirect(url_for('static', filename='images/' + filename), code=301)

if __name__ == '__main__':
    app.run(debug=True, port=8000)