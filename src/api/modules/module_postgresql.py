import psycopg2 as ps
from psycopg2 import sql
import os
from dotenv import load_dotenv
from .module_logger import log_function

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

    def __eq__(self, user):
        return user.user_id == self.user_id and user.user_name == self.user_name

    def __empty__(self):
        return self.user_id < 0

    def __dict__(self):
        return {"user_id": self.user_id, "user_name": self.user_name, "deck_ids": self.deck_ids}
    
    def __str__(self):
        return self.__dict__().__str__()

TABLE_COL_NAMES = ['user_name','password','deck_ids']

# db connection settings
DB_SETTINGS = {
        'database'        : os.getenv("DB_NAME"),
        'user'            : os.getenv("DB_USER"),
        'host'            : os.getenv("DB_HOST"),
        'password'        : os.getenv("DB_PASS"),
        'port'            : os.getenv("DB_PORT"),
        'application_name': 'sqs_2025'
    }

# INPUT CHECK
def check_passwd_input(password: str, function_name="check_passwd_input") -> int:
    if not isinstance(password, str):
        log_function(MODULE_NAME, function_name, "Password must be a string", "error")
        return 10

    if not len(password) > 7:
        log_function(MODULE_NAME, function_name, "Password must contain at least 8 character", "warn")
        return 11
    
    if not any(char.isdigit() for char in password):
        log_function(MODULE_NAME, function_name, "Password must contain at least one digit", "warn")
        return 12
    
    if not any(char.isupper() for char in password):
        log_function(MODULE_NAME, function_name, "Password must contain at least one upper character", "warn")
        return 13
    
    log_function(MODULE_NAME, function_name, "Password check was successful")
    return 0

# check user input
def check_user_input(user_name: str, function_name="check_user_input") -> int:
    if not isinstance(user_name, str):
        log_function(MODULE_NAME, function_name, "Username must be of type string", "Error")
        return 4

    if not len(user_name) > 0:
        log_function(MODULE_NAME, function_name, "Username must not be empty", "Error")
        return 5
    if not user_name[0].isalpha():
        log_function(MODULE_NAME, function_name, "Username must start with a letter", "Error")
        return 6
    log_function(MODULE_NAME, function_name, "Username check was successful")
    return 0

# check deck ids input
def check_deck_ids_input(deck_ids: list[int], function_name="check_deck_ids_input") -> int:
    # more indepth check maybe
    if not isinstance(deck_ids, list):
        log_function(MODULE_NAME, function_name, "deck_ids must be of type list", "Error")
        return 7
    deck_len = len(deck_ids)
    if deck_len > 0:
        for i in range(0, deck_len):
            try:
                deck_ids[i] = int(deck_ids[i])
            except ValueError:
                log_function(MODULE_NAME, function_name, "deck_ids list must contain digits only", "Error")
                return 8
    log_function(MODULE_NAME, function_name, "Deck_Ids check was successful")
    return 0


def get_postgress_conn(db_settings: dict):
    function_name="get_postgress_conn"

    try:
        log_function(MODULE_NAME, function_name, "Try connecting to database")
        conn = ps.connect(**db_settings)
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
        return 1
    
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
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Cleaning table {table_name} failed. Error: {e.__str__()}", "error")
        conn.rollback()
        return 2


def delete_table(conn, table_name="users") -> int:
    function_name="delete_table"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Deleting table with name {table_name} failed. Error: Connection to DB missing.", "error")
        return 1
    
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
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Deleting table {table_name} failed. Error: {e.__str__()}", "error")
        return 2


def add_user_with_crypt_pass(conn, user_name, passwd, deck_ids, table_name="users") -> int:
    function_name="add_user_with_crypt_pass"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Adding user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1
    
    passwd_check = check_passwd_input(passwd, function_name)
    if not passwd_check == 0:
        return passwd_check # error >= 10 for password error

    user_name_check = check_user_input(user_name, function_name)
    if not user_name_check == 0:
        return user_name_check

    deck_ids_check = check_deck_ids_input(deck_ids, function_name)
    if not deck_ids_check == 0:
        return deck_ids_check

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
        cursor.execute(query_base, [user_name, passwd, deck_ids])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Added user {user_name} successfully")
        return 0
    except ps.errors.UniqueViolation as e:
        log_function(MODULE_NAME, function_name, f"Adding user {user_name} failed. Error: User already exists!!!", "error")
        conn.rollback()
        return 3
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Creating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return 2


def get_user_from_db(conn, user_name: str, user_password: str, table_name="users") -> UserObj:
    function_name="get_user_from_db"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Fetching user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return UserObj.create_empty()
    
    passwd_check = check_passwd_input(user_password, function_name)
    if not passwd_check == 0:
        return UserObj.create_empty() # error >= 10 for password error

    user_name_check = check_user_input(user_name, function_name)
    if not user_name_check == 0:
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


def update_user_from_db(conn, user_name: str, deck_ids: list[int], table_name="users"):
    function_name="update_user_from_db"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Updating user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1

    user_name_check = check_user_input(user_name, function_name)
    if not user_name_check == 0:
        return user_name_check
    
    deck_ids_check = check_deck_ids_input(deck_ids, function_name)
    if not deck_ids_check == 0:
        return deck_ids_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to update user {user_name}")
        query_base = sql.SQL("""UPDATE {table_name} 
                             SET {col_3} = %s 
                             WHERE {col_1} = %s
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_3=sql.Identifier(TABLE_COL_NAMES[2])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [deck_ids, user_name])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Updated user {user_name} successfully")
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Updating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return 2


def delete_user_from_db(conn, user_name: str, table_name="users"):
    function_name="delete_user_from_db"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Deleting user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1

    user_name_check = check_user_input(user_name)
    if not user_name_check == 0:
        return user_name_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to delete user {user_name}")
        query_base = sql.SQL("""DELETE FROM {table_name}
                             WHERE {col_1} = %s
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Deleted user {user_name} successfully")
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Deleting user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return 2

def close_connection(conn) -> int:
    function_name="close_connection"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: Connection to DB missing.", "error")
        return 1
    
    try:
        log_function(MODULE_NAME, function_name, "Closing database connection")
        conn.close()
        log_function(MODULE_NAME, function_name, "Closed database connection successfully")
        return 0
    except ps.OperationalError as e:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: {e.__str__()}", "error")
        return 2