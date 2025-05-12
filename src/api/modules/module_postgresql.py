import psycopg2 as ps
from psycopg2 import sql
import os
from dotenv import load_dotenv
from .module_logger import log_function

load_dotenv()

MODULE_NAME="module_posgresql"

class DatabaseError(Exception):
    def __init__(self, err_msg=""):
        super().__init__(err_msg)

class UserObj():
    """ 
        This class represents a User entry in the database

        Attributes:
            user_id (str): the id of the user inside the database (auto generated)
            user_name (str): the name of the user
            deck_ids (list): list of integer containing pokemon ids. This represents the card deck of a user

        Methods:
            create_empty: creates empty user with id -1
            __eq__: compairs two userobjects (compairs the __str__() method -> ALL ATTRIBUTES HAVE TO BE EQUAL)
            __dict__: returns the user object as a dictionary
            __str__: returns the user object as a string containing the dictionary
    """
    def __init__(self, user_id: str, user_name: str, deck_ids = None):
        self.user_id = user_id
        self.user_name = user_name
        if deck_ids is None:
            self.deck_ids = []
        else:
            self.deck_ids = deck_ids

    @classmethod
    def create_empty(cls):
        return cls(-1, "")

    def __eq__(self, user):
        return self.__str__() == user.__str__()

    def __empty__(self):
        return self.user_id < 0

    def __dict__(self):
        return {"user_id": self.user_id, "user_name": self.user_name, "deck_ids": self.deck_ids}
    
    def __str__(self):
        return self.__dict__().__str__()

# declaere column names of table
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
    """ Check the password input if it is correct

        Args:
            password (str): The password that will be checked
            function_name (str): The name of the function that calls this check. Defaults to check_passwd_input. (For logging only)

        Returns:
            int: 0 if check succesfull. 10 -> password not a string. 11 -> password < 8. 12 -> Must contain digit. 13 -> Must contain upper character.
    """
    # check if password is a string
    if not isinstance(password, str):
        log_function(MODULE_NAME, function_name, "Password must be a string", "error")
        return 10

    # check password length
    if len(password) <= 7:
        log_function(MODULE_NAME, function_name, "Password must contain at least 8 character", "warn")
        return 11
    
    # check if password contains a digit
    if not any(char.isdigit() for char in password):
        log_function(MODULE_NAME, function_name, "Password must contain at least one digit", "warn")
        return 12
    
    # check if password contains upper character
    if not any(char.isupper() for char in password):
        log_function(MODULE_NAME, function_name, "Password must contain at least one upper character", "warn")
        return 13
    
    log_function(MODULE_NAME, function_name, "Password check was successful")
    return 0

# check user input
def check_user_input(user_name: str, function_name="check_user_input") -> int:
    """ Check the username is correct

        Args:
            user_name (str): The username that will be checked
            function_name (str): The name of the function that calls this check. Defaults to check_user_input. (For logging only)

        Returns:
            int: 0 if check succesfull. 4 -> username must be string. 5 -> username is empty. 6 -> Must start with a letter.
    """
    # check if username is of type string
    if not isinstance(user_name, str):
        log_function(MODULE_NAME, function_name, "Username must be of type string", "Error")
        return 4

    # check if username is empty
    if len(user_name) <= 0:
        log_function(MODULE_NAME, function_name, "Username must not be empty", "Error")
        return 5
    # check if username starts with a letter
    if not user_name[0].isalpha():
        log_function(MODULE_NAME, function_name, "Username must start with a letter", "Error")
        return 6
    log_function(MODULE_NAME, function_name, "Username check was successful")
    return 0

# check deck ids input
def check_deck_ids_input(deck_ids: list[int], function_name="check_deck_ids_input") -> int:
    """ Check the deck_ids input if it is correct

        Args:
            deck_ids (list[int]): The deck_ids that will be checked
            function_name (str): The name of the function that calls this check. Defaults to check_deck_ids_input. (For logging only)

        Returns:
            int: 0 if check succesfull. 7 -> deck_ids is empty. 8 -> the list must contain integer only.
    """
    # check if deckid is of type list
    if not isinstance(deck_ids, list):
        log_function(MODULE_NAME, function_name, "deck_ids must be of type list", "Error")
        return 7
    # check if list is empty and if list contains elements that are not integer. If element is str but contains only a digit convert it to int
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
    """ Create connection to a postgress database using the given settings

        Args:
            db_settings (dict): settings for connection

        Returns:
            psycogp2.Connection | None: Returns a connection object if connection was successful. Returns None type object otherwise
    """
    function_name="get_postgress_conn"

    # try creating connection using the settings
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
    """ Create a table inside the database

        Args:
            conn: Connection object must not be None type
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Creating table failed.
    """
    function_name="create_table"

    if conn is None:
        log_function(MODULE_NAME, function_name, f"Creating table {table_name} failed. Error: Connection to DB missing", "error")
        return 1
    
    try:
        # create SQL query base (SQL Injection secure)
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

        # get cursor and execute querry
        cursor = conn.cursor()
        log_function(MODULE_NAME, function_name, f"Try creating table with name {table_name}")
        cursor.execute(query_base)

        # commit the changes to database
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Successfully created table with name {table_name}")
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Creating users table failed. Error: {e.__str__()}", "error")
        return 2


def clean_table(conn, table_name="users"):
    """ Clean a table inside the database

        Args:
            conn: Connection object must not be None type
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Cleaning table failed.
    """
    function_name="clean_table"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Cleaning table with name {table_name} failed. Error: Connection to DB missing.", "error")
        return 1
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to clean table with name {table_name}")

        # create querry. get current courser of database, execute querry and commit changes
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
        # rollback commit to be able to commit another querry
        conn.rollback()
        return 2


def delete_table(conn, table_name="users") -> int:
    """ Delete a table inside the database

        Args:
            conn: Connection object must not be None type
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Deleting table failed.
    """
    function_name="delete_table"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Deleting table with name {table_name} failed. Error: Connection to DB missing.", "error")
        return 1
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to delete table with name {table_name}")
        
        # create querry. get current courser of database, execute querry and commit changes
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
    """ Add a new user to a table inside the database

        Args:
            conn: Connection object must not be None type
            user_name (str): the name of the user
            passwd (str): the password of the user
            deck_ids (list[int]): list containing pokemon ids that resemble the deck of the user
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Deleting table failed.
                 4 -> username must be string. 5 -> username is empty. 6 -> Must start with a letter.
                 7 -> deck_ids is empty. 8 -> the list must contain integer only.
                 10 -> password not a string. 11 -> password < 8. 12 -> Must contain digit. 13 -> Must contain upper character.
    """
    function_name="add_user_with_crypt_pass"

    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Adding user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1
    
    # check input
    passwd_check = check_passwd_input(passwd, function_name)
    if passwd_check != 0:
        return passwd_check # error >= 10 for password error

    user_name_check = check_user_input(user_name, function_name)
    if user_name_check != 0:
        return user_name_check

    deck_ids_check = check_deck_ids_input(deck_ids, function_name)
    if deck_ids_check != 0:
        return deck_ids_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to add user {user_name}")
        
        col_names = sql.SQL(', ').join(sql.Identifier(n) for n in TABLE_COL_NAMES )
        # create querry. get current courser of database, execute querry and commit changes
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
    """ Returns a user from a table inside the database

        Args:
            conn: Connection object must not be None type
            user_name (str): the name of the user
            passwd (str): the password of the user
            table_name (str): Name of the table. Default is "users"

        Returns:
            UserObj: Returns empty user with id -1 if fetch fails. Returns UserObj containing user information otherwise.
    """
    function_name="get_user_from_db"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Fetching user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return UserObj.create_empty()
    
    # check input
    passwd_check = check_passwd_input(user_password, function_name)
    if passwd_check != 0:
        return UserObj.create_empty() # error >= 10 for password error

    user_name_check = check_user_input(user_name, function_name)
    if user_name_check != 0:
        return UserObj.create_empty()
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to fetch user {user_name}")
        # create querry. get current courser of database, execute querry and commit changes
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
        # check if the fetch was successful -> User exists or not?
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
    """ Update a user from a table inside the database

        Args:
            conn: Connection object must not be None type
            user_name (str): the name of the user
            deck_ids (list[int]): list containing pokemon ids that resemble the deck of the user
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Deleting table failed.
                 4 -> username must be string. 5 -> username is empty. 6 -> Must start with a letter.
                 7 -> deck_ids is empty. 8 -> the list must contain integer only.
    """
    function_name="update_user_from_db"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Updating user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1

    # check input
    user_name_check = check_user_input(user_name, function_name)
    if user_name_check != 0:
        return user_name_check
    
    deck_ids_check = check_deck_ids_input(deck_ids, function_name)
    if deck_ids_check != 0:
        return deck_ids_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to update user {user_name}")
        # create querry. get current courser of database, execute querry and commit changes
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
    """ Delete a user from a table inside the database

        Args:
            conn: Connection object must not be None type
            user_name (str): the name of the user
            table_name (str): Name of the table. Default is "users"

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Deleting table failed.
                 4 -> username must be string. 5 -> username is empty. 6 -> Must start with a letter.
    """
    function_name="delete_user_from_db"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Deleting user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return 1

    # check input
    user_name_check = check_user_input(user_name)
    if user_name_check != 0:
        return user_name_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to delete user {user_name}")
        # create querry. get current courser of database, execute querry and commit changes
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
    """ Close the connection to the database

        Args:
            conn: Connection object must not be None type

        Returns:
            int: 0 if successful. 1 -> None Type connection. 2 -> Deleting table failed.
    """
    function_name="close_connection"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        "Closing database connection failed. Error: Connection to DB missing.", "error")
        return 1
    
    try:
        # close connection
        log_function(MODULE_NAME, function_name, "Closing database connection")
        conn.close()
        log_function(MODULE_NAME, function_name, "Closed database connection successfully")
        return 0
    except ps.OperationalError as e:
        log_function(MODULE_NAME, function_name, 
        f"Closing database connection failed. Error: {e.__str__()}", "error")
        return 2