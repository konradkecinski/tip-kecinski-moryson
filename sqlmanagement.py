import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_tables(db_file):
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            name text NOT NULL,
                                            passwd text NOT NULL,
                                            mail text NOT NULL,
                                            creation_timestamp DATETIME,
                                            last_login DATETIME ); """

    sql_create_friends_table = """CREATE TABLE IF NOT EXISTS friends (
                                        id_user  integer NOT NULL,
                                        id_friend integer NOT NULL,
                                        approved BOOLEAN NOT NULL CHECK (approved IN (0,1)),
                                        timestamp DATETIME,
                                        FOREIGN KEY (id_user) REFERENCES users (id)
                                        FOREIGN KEY (id_friend) REFERENCES users (id)
                                    );"""

    conn = sqlite3.connect(db_file)

    # create tables
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql_create_users_table)
            c = conn.cursor()
            c.execute(sql_create_friends_table)
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")


def select_all(db_file):
        sql_users = """ SELECT * FROM users; """
        sql_friends = """ SELECT * FROM friends; """
        conn = sqlite3.connect(db_file)
        if conn is not None:
            try:
                c = conn.cursor()
                c.execute(sql_users)
                print(c.fetchall())
                c = conn.cursor()
                c.execute(sql_friends)
                print(c.fetchall())
            except Error as e:
                print(e)
        else:
            print("Error! cannot create the database connection.")

def delete_user(db_file, id):
    sql = """ DELETE FROM users WHERE id = {0}; """.format(id)
    print(sql)
    conn = sqlite3.connect(db_file)
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql)
            conn.commit()
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    #create_connection(r"database.db")
    #create_tables(r"database.db")
    #delete_user(r"database.db",6)
    select_all(r"database.db")