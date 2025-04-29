import psycopg2 as ps
import os
from dotenv import load_dotenv
from .module_logger import log_function

load_dotenv()

MODULE_NAME="module_posgresql"

class DatabaseError(Exception):
    def __init__(self, err_msg=""):
        raise Exception(err_msg)

def get_postgress_conn():
    function_name="get_postgress_conn"

    DATABASE = os.getenv("DB_NAME")
    HOST = os.getenv("DB_HOST")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASS")
    PORT = os.getenv("DB_PORT")

    try:
        log_function(MODULE_NAME, function_name, "Try connecting to database")
        conn = ps.connect(database=DATABASE,
                                host=HOST,
                                user=USER,
                                password=PASSWORD,
                                port=PORT)
        log_function(MODULE_NAME, function_name, "Connected to database successfully")
        return conn
    except ps.OperationalError as e:
        # log e
        log_function(MODULE_NAME, function_name, f"Connecting to database failed. Error: {e.__str__()}", "error")
        return None

def create_table(conn, table_name="users"):
    function_name="create_table"

    if conn is None:
        log_function(MODULE_NAME, function_name, f"Creating users table failed. Error: Connection to DB missing", "error")
        return False
    
    try:
        cursor = conn.cursor()
        log_function(MODULE_NAME, function_name, f"Try creating table with name {table_name}")
        create=f"""CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE TABLE IF NOT EXISTS {table_name} (
            id INT GENERATED ALWAYS AS IDENTITY,
            user_name VARCHAR(255) NOT NULL, 
            password TEXT NOT NULL,
            deck_ids INTEGER[]
        )"""
        cursor.execute(create)
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Successfully created table with name {table_name}")
        return True
    except Exception as e:
        log.error()
        log_function(MODULE_NAME, function_name, f"Creating users table failed. Error: {e.__str__()}", "error")
        return False


def clean_table(conn, table_name="users"):
    function_name="clean_table"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Cleaning table with name {table_name} failed. Error: Connection to DB missing.", "error")
        return False
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to clean table with name {table_name}")
        cursor = conn.cursor()
        clean=f"TRUNCATE {table_name};"
        cursor.execute(clean)
        conn.commit()
        log.info("Succesfully cleaned users table")
        log_function(MODULE_NAME, function_name, f"Cleaned table {table_name} successfully")
        return True
    except Exception as e:
        log_function(MODULE_NAME, function_name, f"Cleaning table {table_name} failed. Error: {e.__str__()}", "error")
        return False


def delete_table(conn, table_name="users"):
    function_name="delete_table"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Deleting table with name {table_name} failed. Error: Connection to DB missing.", "error")
        return False
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to delete table with name {table_name}")
        cursor = conn.cursor()
        clean=f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(clean)
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Deleted table {table_name} successfully")
        return True
    except Exception as e:
        log_function(MODULE_NAME, function_name, f"Deleting table {table_name} failed. Error: {e.__str__()}", "error")
        return False


def add_user_with_crypt_pass(conn, user_name, passwd, poke_id_list, table_name="users"):
    function_name="add_user_with_crypt_pass"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Adding user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return False
    
    # check input!!!

    try:
        # check if user already exists
        
        log_function(MODULE_NAME, function_name, f"Trying to add user {user_name}")
        sql = f""" INSERT INTO {table_name} (user_name, password, deck_ids) VALUES (
            {user_name},
            crypt({passwd}, gen_salt('md5')),
            {poke_id_list}
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Added user {user_name} successfully")
    except Exception as e:
        log_function(MODULE_NAME, function_name, f"Deleting table {table_name} failed. Error: {e.__str__()}", "error")
        return False


def user_with_crypt_pass(conn):
    if conn is None:
        log.error("Creating user failed. Error: Connection to DB missing")
        return
    
    sql = """ INSERT INTO DB_TEST (user_name, password) VALUES (
            'tsuna',
            crypt('tsunapasswd', gen_salt('md5'))
        );
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    log.info("Succesfully added test-user tsuna")

def get_user_tst(conn, passwd):
    if conn is None:
        log.error("Receiving users from db failed. Error: Connection to DB missing")
        return
    
    sql = f""" SELECT id FROM DB_TEST
            WHERE user_name = 'tsuna' 
            AND password = crypt('{passwd}', password);
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    
    users = cursor.fetchall()
    
    conn.commit()
    return users


def close_connection(conn):
    function_name="close_connection"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: Connection to DB missing.", "error")
    
    try:
        log_function(MODULE_NAME, function_name, "Closing database connection")
        conn.close()
        log_function(MODULE_NAME, function_name, "Closed database connection successfully")
    except pb.OperationalError:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: {e.__str__()}", "error")