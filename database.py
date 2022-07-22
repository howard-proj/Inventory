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

        # Create the users table
        self.execute("""CREATE TABLE Users(
            Id INT,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0);
        """)
        self.commit()

        self.execute("""CREATE TABLE Inventory(
            Id INT,
            itemname TEXT,
            quantity INT);
        """)
        self.commit()

    def count(self, table):
        sql_cmd = """
                SELECT *
                FROM {table}
            """.format(table=table)
        self.execute(sql_cmd)
        count = len(self.cur.fetchall())
        return count

    def check_credentials(self, username, password):
        sql_query = """
                SELECT username, password
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """.format(username=username, password=password)
        self.execute(sql_query)
        # If our query returns
        temp = self.cur.fetchone()
        if temp:
            return temp
        else:
            return False

    def add_users(self, username, password, admin=0):
        count = self.count("Users")+1
        sql_cmd = """
                INSERT INTO Users
                VALUES({id}, '{username}', '{password}', {admin})
            """.format(id=count,username=username, password=password, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    def add_invetory(self, itemname, quantity):
        count = self.count("Inventory")+1
        sql_cmd = """
                INSERT INTO Inventory
                VALUES({id}, '{itemname}', {quantity})
            """.format(id=count,itemname=itemname, quantity=quantity)
            
        self.execute(sql_cmd)
        self.commit()
        return True


    def select_all_users(self):
        sql_query = """
                SELECT *
                FROM Users
            """
        self.execute(sql_query)
        return self.cur.fetchall()

    def select_all_item(self):
        sql_query = """
                SELECT *
                FROM Inventory
            """
        self.execute(sql_query)
        return self.cur.fetchall()

