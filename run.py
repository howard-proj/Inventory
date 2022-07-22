import database
from flask import Flask, redirect, render_template, flash, url_for, request
from modules import *

user_details = {}
session = {}
page = {}

myDatabase = database.SQLDatabase()
myDatabase.database_setup()
myDatabase.add_users('kanday', 'bos123', 1)

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

        print("OVER HERE")
        print(login_data)
        global user_details
        user_details = login_data[0]

        return redirect(url_for('home'))

    elif(request.method == 'GET'):
        return render_template("login.html", page=page)

@app.route('/logout')
def logout():
    flash("You have logged out")
    return redirect(url_for('index'))

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/inventory')
def get_inventory():
    return render_template("inventory.html")

@app.route('/inventory/create')
def inventory_create():
    return "Creat a new inventory"

@app.route('/inventory/<inventory_id>')
def single_inventory(inventory_id):
    return "single_inventory"


if __name__ == '__main__':
    app.run(debug=True)