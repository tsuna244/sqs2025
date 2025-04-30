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
    def __init__(self, user_id: str, user_name: str, deck_ids = []):
        self.user_id = user_id
        self.user_name = user_name
        self.deck_ids = deck_ids

    @classmethod
    def create_empty(cls):
        return cls(-1, "")

    def __empty__(self):
        return self.user_id < 0

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
        conn.rollback()
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


def add_user_with_crypt_pass(conn, user_name, passwd, poke_id_list, table_name="users") -> int:
    function_name="add_user_with_crypt_pass"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Adding user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return -1
    
    # TODO: password check
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to add user {user_name}")
        
        col_names = sql.SQL(', ').join(sql.Identifier(n) for n in TABLE_COL_NAMES )

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
        return 1
    except ps.errors.UniqueViolation as e:
        log_function(MODULE_NAME, function_name, f"Adding user {user_name} failed. Error: User already exists!!!", "error")
        conn.rollback()
        return -2
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Creating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return -3


def get_user_from_db(conn, user_name: str, user_password: str, table_name="users") -> UserObj:
    function_name="get_user_from_db"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Fetching user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return UserObj.create_empty()
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to fetch user {user_name}")
        
        query_base = sql.SQL("""SELECT id, {col_1}, {col_3} FROM {table_name} 
                             WHERE {col_1} = %s
                             AND {col_2} = crypt(%s, password);
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_2=sql.Identifier(TABLE_COL_NAMES[1]),
        col_3=sql.Identifier(TABLE_COL_NAMES[2])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name, user_password])
        conn.commit()
        fetch = cursor.fetchone()
        if fetch is not None:
            _id, _name, _deck_ids = fetch
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} successfully")
            return UserObj(_id, _name, _deck_ids)
        else:
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} not found", "warn")
            return UserObj.create_empty()
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Fetching user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return UserObj.create_empty()


def close_connection(conn):
    function_name="close_connection"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: Connection to DB missing.", "error")
    
    try:
        log_function(MODULE_NAME, function_name, "Closing database connection")
        conn.close()
        log_function(MODULE_NAME, function_name, "Closed database connection successfully")
    except ps.OperationalError:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: {e.__str__()}", "error")
    

conn = get_postgress_conn()

if clean_table(conn):
    print("Table clean")

if create_table(conn):
    add_user_with_crypt_pass(conn, "tsuna", "1234", [1, 2, 3, 4])
    add_user_with_crypt_pass(conn, "tsuna", "1234", [2, 4, 5, 6]) # check output if this happens
    test_user = get_user_from_db(conn, "orhan", "1234")
    if test_user.__empty__():
        print("test user empty")
    else:
        print("test user not empty")
    
if delete_table(conn):
    print("table gone")

