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
        self.execute("DROP TABLE IF EXISTS Images")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0)
        """)
        self.commit()

        self.execute("""CREATE TABLE Inventory(
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventoryname TEXT,
            quantity INT,
            description TEXT)
        """)
        self.commit()

        self.execute("""CREATE TABLE Images(
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER REFERENCES Inventory(inventory_id) NOT NULL,
            filename TEXT)
        """)

        self.execute("""
            INSERT INTO Users(username, password, admin) VALUES('kanday', 'bos123', 1);
            INSERT INTO Users(username, password, admin) VALUES('biasa', 'bisa123', 0);

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Nevada', 2, 'Karton');
            INSERT INTO Images(inventory_id, filename) VALUES(1, 'nevada.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Jk-100', 3, 'Karton');
            INSERT INTO Images(inventory_id, filename) VALUES(2, 'jk-100.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('GPR263', 3, 'Karton');
            INSERT INTO Images(inventory_id, filename) VALUES(3, 'gpr263.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Label Jerry 99', 2, 'Gross');
            INSERT INTO Images(inventory_id, filename) VALUES(4, 'label-jerry.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('TD-103', 4, 'Gross');
            INSERT INTO Images(inventory_id, filename) VALUES(5, 'td-103.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Gunting Kecil Emigo', 2, 'Gross');
            INSERT INTO Images(inventory_id, filename) VALUES(6, 'gunting-kecil.png');

            INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Gunting Besar Emigo', 2, 'Gross');
            INSERT INTO Images(inventory_id, filename) VALUES(7, 'gunting-besar.png');
        """)
        self.commit()

        # INSERT INTO Inventory(inventoryname, quantity, description) VALUES('24mm merah', 3, 'Karton');
        #     INSERT INTO Inventory(inventoryname, quantity, description) VALUES('24mm biru', 5, 'Karton');
        #     INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Lakban Bening Merah', 2, 'Karton');
        #     INSERT INTO Inventory(inventoryname, quantity, description) VALUES('Lakban Coklat Merah', 3, 'Karton');
        #     INSERT INTO Inventory(inventoryname, quantity, description) VALUES('12mm Merah', 3, 'Karton');
        #     INSERT INTO Inventory(inventoryname, quantity, description) VALUES('12mm Biru', 5, 'Karton');
        
    def check_credentials(self, username, password):
        sql_query = """
                SELECT username, password, admin
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
                VALUES('{username}', '{password}', {admin});
            """.format(username=username, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    def add_inventory(self, inventoryname, quantity, description, filename='notfound.png'):
        # Equivalent to following query:
        # WITH ins1 AS (
        #     INSERT INTO Inventory(inventoryname, quantity, description)
        #     VALUES({inventoryname}, {quantity}, {description})
        #     RETURNING inventory_id
        # )
        # INSERT INTO Images(inventory_id, {filename})
        # SELECT inventory_id FROM ins1;
        #
        # Note: Sqlite3 does not support INSERT subquery
        sql_cmd = """
            INSERT INTO Inventory(inventoryname, quantity, description)
            VALUES('{inventoryname}', {quantity}, '{description}')
            """.format(inventoryname=inventoryname, quantity=quantity, description=description)
        self.execute(sql_cmd)

        last_id = self.cur.lastrowid
        sql_cmd = """
            INSERT INTO Images(inventory_id, filename)
            VALUES({last_id}, '{filename}')
        """.format(last_id=last_id, filename=filename)
        self.execute(sql_cmd)
        self.commit()

        return True
    
    def update_inventory(self, inventory_id, inventoryname, quantity, description):
        sql_cmd = """
                UPDATE Inventory
                SET inventoryname = '{inventoryname}', quantity = {quantity}, description = '{description}'
                WHERE inventory_id = {inventory_id}
            """.format(inventory_id=inventory_id, inventoryname=inventoryname, quantity=quantity, description=description)
        self.execute(sql_cmd)
        self.commit()
        return True

    def select_all_images(self):
        sql_query = """
                SELECT image_id, inventory_id, filename
                FROM Images
                ORDER BY image_id
            """
        ## Returning in JSON format
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    def select_all_users(self):
        sql_query = """
                SELECT user_id, username, password, admin
                FROM Users
                ORDER BY user_id
            """
        ## Returning in JSON format
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    def select_all_inventories(self):
        sql_query = """
                SELECT inv.inventory_id, inv.inventoryname, inv.quantity, inv.description, im.filename
                FROM Inventory inv INNER JOIN Images im
                ON inv.inventory_id = im.inventory_id
                ORDER BY inv.inventory_id
            """
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
                SELECT inv.inventory_id, inv.inventoryname, inv.quantity, inv.description, im.filename
                FROM Inventory inv INNER JOIN Images im 
                ON inv.inventory_id = im.inventory_id
                Where inv.inventory_id = {inventory_id}
            """.format(inventory_id=inventory_id)
        ## Returning things in JSON format
        result = []
        self.execute(sql_query)
        cols = [a[0] for a in self.cur.description]
        returning = self.cur.fetchall()
        for row in returning:
            result.append({a:b for a,b in zip(cols, row)})
        return result

    
# myDatabase = SQLDatabase()
# myDatabase.database_setup()
# myDatabase.add_users("Kanday", "bos123", 1)
# myDatabase.add_inventory("Nevada", 120, "Lusin")
# print(myDatabase.select_all_inventories()[7])
# print(myDatabase.select_all_images()[7])

# print(myDatabase.select_inventory(1))
# print(myDatabase.select_all_users())
