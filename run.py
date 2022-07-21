import database
from flask import Flask, redirect, render_template, flash, url_for
from modules import *

user_details = {}
session = {}
page = {}

myDatabase = database.SQLDatabase()

app = Flask(__name__)

@app.route('/', methods=["GET"])
@app.route('/login', methods=["GET"])
def get_login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    flash("You have logged out")
    return redirect(url_for('index'))

@app.route('/home')
def get_home():
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