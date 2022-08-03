import database
from flask import Flask, redirect, render_template, flash, url_for, request
from modules import *

user_details = {}
session = {}
page = {}

myDatabase = database.SQLDatabase()
myDatabase.database_setup()
myDatabase.add_users('kanday', 'bos123', 1)

myDatabase.add_inventory("Nevada", 120)

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

    page['title'] = 'Movie Creation'

    movies = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('movie_title' not in request.form):
            newdict['movie_title'] = 'Empty Film Value'
        else:
            newdict['movie_title'] = request.form['movie_title']
            print("We have a value: ",newdict['movie_title'])

        if ('release_year' not in request.form):
            newdict['release_year'] = '0'
        else:
            newdict['release_year'] = request.form['release_year']
            print("We have a value: ",newdict['release_year'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('storage_location' not in request.form):
            newdict['storage_location'] = 'Empty storage location'
        else:
            newdict['storage_location'] = request.form['storage_location']
            print("We have a value: ",newdict['storage_location'])

        if ('film_genre' not in request.form):
            newdict['film_genre'] = 'drama'
        else:
            newdict['film_genre'] = request.form['film_genre']
            print("We have a value: ",newdict['film_genre'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])
        
        print('newdict is:')
        print(newdict)

        #forward to the database to manage insert
        # movies = database.add_movie_to_db(newdict['movie_title'],newdict['release_year'],newdict['description'],newdict['storage_location'],newdict['film_genre'])


        max_movie_id = database.get_last_movie()[0]['movie_id']
        print(movies)
        if movies is not None:
            max_movie_id = movies[0]

        # ideally this would redirect to your newly added movie
        return single_movie(max_movie_id)
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