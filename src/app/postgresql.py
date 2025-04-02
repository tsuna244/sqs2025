import psycopg2 as ps
import os
from dotenv import load_dotenv

load_dotenv()

def get_postgress_conn():
    DATABASE = os.getenv("DB_NAME")
    HOST = os.getenv("DB_HOST")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASS")
    PORT = os.getenv("DB_PORT")
    
    try:
        return ps.connect(database=DATABASE,
                                host=HOST,
                                user=USER,
                                password=PASSWORD,
                                port=PORT)

        #cursor.execute("SELECT * FROM DB_table WHERE id = 1")

        # outputs only first line of result
        #print(cursor.fetchone())

        # outputs all lines of result
        #print(cursor.fetchall())
        print("worked")
        # ouputs first 3 lines ouf result
        #print(cursor.fetchmany(size=3))
    except ps.OperationalError as e:
        # log e
        print(str(e))
        return None

def create_table(conn):
    if conn is None:
        print("Connection is None")
        return
    
    cursor = conn.cursor()
    Name = "DB_TEST"
    create=f"""CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE TABLE IF NOT EXISTS {Name} (
        id INT GENERATED ALWAYS AS IDENTITY,
        user_name VARCHAR(255) NOT NULL, 
        password TEXT NOT NULL,
        deck_ids INTEGER[]
    )"""
    cursor.execute(create)
    conn.commit()
    print("Create Table Done")

def clean_table(conn, table_name: str):
    if conn is None:
        print("Connection is None")
        return
    
    cursor = conn.cursor()
    clean=f"TRUNCATE {table_name};"
    cursor.execute(clean)
    conn.commit()
    print("Clean Table Done")

def delete_table(conn, table_name):
    if conn is None:
        print("Connection is None")
        return
    
    cursor = conn.cursor()
    clean=f"DROP TABLE IF EXISTS {table_name};"
    cursor.execute(clean)
    conn.commit()
    print("Drop Table Done")

def user_with_crypt_pass(conn):
    if conn is None:
        print("Connection is None")
        return
    
    sql = f""" INSERT INTO DB_TEST (user_name, password) VALUES (
            'tsuna',
            crypt('tsunapasswd', gen_salt('md5'))
        );
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    print("Added User Tsuna")

def get_user_tst(conn, passwd):
    if conn is None:
        print("Connection is None")
        return
    sql = f""" SELECT id FROM DB_TEST
            WHERE user_name = 'tsuna' 
            AND password = crypt('{passwd}', password);
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    print(cursor.fetchall())
    
    conn.commit()
    print("test User Tsuna")


conn = get_postgress_conn()
create_table(conn)
#delete_table(conn, "DB_TEST")

user_with_crypt_pass(conn)
get_user_tst(conn, "tsunapasswd")
get_user_tst(conn, "wrongpass")

conn.close()