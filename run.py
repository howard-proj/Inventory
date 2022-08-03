import database
from flask import Flask, redirect, render_template, flash, url_for, request
from modules import *

user_details = {}
session = {}
page = {}

myDatabase = database.SQLDatabase()
myDatabase.database_setup()
myDatabase.add_users('kanday', 'bos123', 1)

myDatabase.add_inventory("Nevada", 2, "Karton")
myDatabase.add_inventory("JK-100", 3, "Karton")
myDatabase.add_inventory("GPR263", 3, "Karton")
myDatabase.add_inventory("Label Jerry", 1, "Gross")
myDatabase.add_inventory("TD-103", 4, "Pcs")
myDatabase.add_inventory("12mm Biru", 7, "Karton")
myDatabase.add_inventory("12mm Merah", 1, "Karton")
myDatabase.add_inventory("Gunting Kecil Emigo", 0, "Karton")
myDatabase.add_inventory("Gunting Besar Emigo", 0, "Karton")
myDatabase.add_inventory("Lakban Merah Bening", 5, "Karton")
myDatabase.add_inventory("Lakban Biru Bening", 5, "Karton")
myDatabase.add_inventory("24mm Biru", 8, "Karton")
myDatabase.add_inventory("24mm Merah", 7, "Karton")
myDatabase.add_inventory("Frixion 0.5 Hitam", 6, "Gross")

app = Flask(__name__)
app.secret_key = """U29tZWJvZHkgb25jZSB0b2xkIG1lIFRoZSB3b3JsZCBpcyBnb25uYSBy
b2xsIG1lIEkgYWluJ3QgdGhlIHNoYXJwZXN0IHRvb2wgaW4gdGhlIHNoZWQgU2hlIHdhcyBsb29r
aW5nIGtpbmRhIGR1bWIgV2l0aCBoZXIgZmluZ2VyIGFuZCBoZXIgdGh1bWIK"""

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
    
    return render_template("home.html", 
                            page=page,
                            session=session,
                            user=user_details)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    page['bar'] = True
    flash("You have logged out")
    return redirect(url_for('home'))
    

@app.route('/inventories')
def list_inventories():
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('/login'))

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
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Inventory creation'

    movies = None
    print("request form is:")
    newdict = {}
    print(request.form)

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


        # if ('artwork' not in request.form):
        #     newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        # else:
        #     newdict['artwork'] = request.form['artwork']
        #     print("We have a value: ",newdict['artwork'])
        
        
        print('newdict is:')
        print(newdict)

        #forward to the database to manage insert
        myDatabase.add_inventory(newdict['inventoryname'],newdict['quantity'],newdict['description'])

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

if __name__ == '__main__':
    app.run(debug=True)