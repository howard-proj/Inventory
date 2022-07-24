import sqlite3


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    # Get the database running
    def __init__(self, database_arg="database.db"):
        try:
            self.conn = sqlite3.connect(database_arg,check_same_thread=False)
        # print(type(self.conn))
        # print(type(self.conn.cursor()))
            self.cur = self.conn.cursor()
        except sqlite3.DatabaseError as e:
            print("database error:{}".format(e))

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except sqlite3.DatabaseError as e:
                print("database error:{}".format(e))
                pass
        return out

    # Commit changes to the database
    def commit(self):
        try:
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            print("database error:{}".format(e))

    # -----------------------------------------------------------------------------

    # Sets up the database
    # Default admin password
    def database_setup(self):

        # # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()
        self.execute("DROP TABLE IF EXISTS Inventory")
        self.commit()
        self.execute("DROP TABLE IF EXISTS MetaDataType")
        self.commit()
        self.execute("DROP TABLE IF EXISTS MetaData")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0);
        """)
        self.commit()

        self.execute("""CREATE TABLE Inventory(
            inventory_id INTEGER PRIMARY KEY REFERENCES Stationery(stationery_id),
            inventoryname TEXT,
            quantity INT);
        """)
        self.commit()

        self.execute("""CREATE Table MetaDataType(
            md_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            md_type_name VARCHAR (100) NOT NULL);
        """)
        self.commit()

        self.execute(""""CREATE TABLE MetaData(
            md_id INTEGER PRIMARY KEY AUTOINCREMENT,
            md_type_id INTEGER REFERENCES MetaDataType(md_type_id) NOT NULL,
            md_value text NOT NULL);
        """)
        self.commit()

        self.execute("""CREATE TABLE Stationery(
            stationery_id INTEGER NOT NULL,
            FOREIGN KEY ()
        )
        """)

    def check_credentials(self, username, password):
        sql_query = """
                SELECT username, password
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """.format(username=username, password=password)

        ##Returning JSON for one entry only
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchone()
        result.append({a:b for a,b in zip(cols, returning)})
        
        return result

    def add_users(self, username, password, admin=0):
        sql_cmd = """
                INSERT INTO Users(username, password, admin)
                VALUES('{username}', '{password}', {admin})
            """.format(username=username, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    def add_inventory(self, inventoryname, quantity):
        sql_cmd = """
                INSERT INTO Inventory(inventoryname, quantity)
                VALUES({id}, '{inventoryname}', {quantity})
            """.format(inventoryname=inventoryname, quantity=quantity)
            
        self.execute(sql_cmd)
        self.commit()
        return True


    def select_all_users(self):
        sql_query = """
                SELECT user_id, password, admin
                FROM Users
                ORDER BY user_id
            """
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    def select_all_inventories(self):
        sql_query = """
                SELECT inventory_id, inventoryname, quantity
                FROM Inventory
                ORDER BY inventory_id
            """
        # self.execute(sql_query)
        ## Returning things in JSON format
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    def select_inventory(self, inventory_id):
        sql_query = """
                SELECT inventory_id, inventoryname, quantity
                FROM Inventory
                Where inventory_id = {inventory_id}
            """.format(inventory_id=inventory_id)
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    

        

# myDatabase = SQLDatabase()
# myDatabase.database_setup()
# myDatabase.add_users('kanday', 'bos123', 1)

# myDatabase.add_inventory("Nevada", 120)

# print(myDatabase.select_all_users())
