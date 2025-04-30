import psycopg2 as ps
from psycopg2 import sql
import os
from dotenv import load_dotenv
#from .module_logger import log_function
from module_logger import log_function # debug only

load_dotenv()

MODULE_NAME="module_posgresql"

class DatabaseError(Exception):
    def __init__(self, err_msg=""):
        raise Exception(err_msg)

class UserObj():
    def __init__(self, user_id, user_name, deck_ids):
        self.user_id = user_id
        self.user_name = user_name
        self.deck_ids = deck_ids

    def __dict__(self):
        return {"user_id": self.user_id, "user_name": self.user_name, "deck_ids": self.deck_ids}
    
    def __str__(self):
        return self.__dict__().__str__()

TABLE_COL_NAMES = ['user_name','password','deck_ids']

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
        query_base = sql.SQL(
            """
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT GENERATED ALWAYS AS IDENTITY,
                {user_name} VARCHAR(255) UNIQUE NOT NULL,
                {password} TEXT NOT NULL,
                {deck_ids} INTEGER[]
            )
            """).format(
                table_name=sql.Identifier(table_name),
                user_name=sql.Identifier(TABLE_COL_NAMES[0]),
                password=sql.Identifier(TABLE_COL_NAMES[1]),
                deck_ids=sql.Identifier(TABLE_COL_NAMES[2])
            )

        cursor = conn.cursor()
        log_function(MODULE_NAME, function_name, f"Try creating table with name {table_name}")
        cursor.execute(query_base)

        conn.commit()
        log_function(MODULE_NAME, function_name, f"Successfully created table with name {table_name}")
        return True
    except ps.Error as e:
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

        query_base = sql.SQL(
            "TRUNCATE {table_name}").format(
                table_name=sql.Identifier(table_name)
            )
        
        cursor = conn.cursor()        
        cursor.execute(query_base)
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Cleaned table {table_name} successfully")
        return True
    except ps.Error as e:
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
        
        query_base = sql.SQL(
            "DROP TABLE IF EXISTS {table_name}").format(
                table_name=sql.Identifier(table_name)
            )
        cursor = conn.cursor()
        cursor.execute(query_base)
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Deleted table {table_name} successfully")
        return True
    except ps.Error as e:
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
        log_function(MODULE_NAME, function_name, f"Trying to add user {user_name}")
        
        col_names = sql.SQL(', ').join(sql.Identifier(n) for n in TABLE_COL_NAMES )
        place_holders = sql.SQL(', ').join(sql.Placeholder() * len(TABLE_COL_NAMES)) # länge der tabelle + 1 (für id)

        query_base = sql.SQL("""insert into {table_name} ({col_names}) values (
            %s,
            crypt(%s, gen_salt('md5')),
            %s
        )""").format(
        table_name=sql.Identifier(table_name),
        col_names=col_names
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name, passwd, poke_id_list])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Added user {user_name} successfully")
    except ps.errors.UniqueViolation as e:
        log_function(MODULE_NAME, function_name, f"Adding user {user_name} failed. Error: User already exists!!!", "error")
        conn.rollback()
        return False
    except ps.Error as e:
        # TODO: check error if user_name already exists
        log_function(MODULE_NAME, function_name, f"Creating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return False


def user_with_crypt_pass(conn):
    if conn is None:
        log_function(MODULE_NAME, function_name, "Creating user failed. Error: Connection to DB missing")
        return
    
    sql_msg = """ INSERT INTO DB_TEST (user_name, password) VALUES (
            'tsuna',
            crypt('tsunapasswd', gen_salt('md5'))
        );
        """
    cursor = conn.cursor()
    cursor.execute(sql_msg)
    conn.commit()
    log_function(MODULE_NAME, function_name, "Succesfully added test-user tsuna")

def get_user_tst(conn, passwd):
    if conn is None:
        log_function(MODULE_NAME, function_name, "Receiving users from db failed. Error: Connection to DB missing")
        return
    
    sql_msg = f""" SELECT id FROM DB_TEST
            WHERE user_name = 'tsuna' 
            AND password = crypt('{passwd}', password);
        """
    cursor = conn.cursor()
    cursor.execute(sql_msg)
    
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
    

conn = get_postgress_conn()

if create_table(conn):
    add_user_with_crypt_pass(conn, "tsuna", "1234", [])
    add_user_with_crypt_pass(conn, "tsuna", "1234", []) # check output if this happens
if delete_table(conn):
    print("table gone")

