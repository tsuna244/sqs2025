import psycopg2 as ps
from psycopg2 import sql
import os
from dotenv import load_dotenv
from .module_logger import log_function
import json

load_dotenv()

MODULE_NAME="module_posgresql"

class DatabaseError(Exception):
    def __init__(self, err_msg=""):
        super().__init__(err_msg)

class UserObj():
    """This class represents a User entry in the database
    
    :param user_id: id of the user inside the database
    :type user_id: int
    :param user_name: name of the user inside the database
    :type user_name: str
    :param deck_ids: list of pokemon ids that represent the deck of the user, defaults to None
    :type deck_ids: list | None
    """
    
    def __init__(self, user_id: str, user_name: str, deck_ids = None, points = None):
        """constructor method
    
        :param user_id: id of the user inside the database
        :type user_id: int
        :param user_name: name of the user inside the database
        :type user_name: str
        :param deck_ids: list of pokemon ids that represent the deck of the user, defaults to None
        :type deck_ids: list | None
        """
        self.user_id = user_id
        self.user_name = user_name
        if deck_ids is None:
            self.deck_ids = []
        else:
            self.deck_ids = deck_ids
        if points is None:
            self.points = 0
        else:
            self.points = points

    @classmethod
    def create_empty(cls):
        """Create empty user object

        :return: `{"user_id": -1, "user_name": "", "deck_ids": None}` -> empty user object with id -1
        :rtype: class: UserObj
        """
        return cls(-1, "")

    def __eq__(self, user):
        return self.__str__() == user.__str__()

    def __empty__(self):
        return self.user_id < 0

    def __dict__(self):
        return {"user_id": self.user_id, "user_name": self.user_name, "deck_ids": self.deck_ids, "points": self.points}
    
    def __str__(self):
        return self.__dict__().__str__()

# declaere column names of table
TABLE_COL_NAMES = ['user_name','password','deck_ids', 'points']

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
    """Check the password input if it is correct

    :param password: The password that will be checked
    :type password: str
    :param function_name: The name of the function that calls this check, defaults to "check_passwd_input"
    :type function_name: str, optional
    :return: `0` if check succesfull, `10` if password not a string, `11` if password length < 8, `12` if no digit in password. `13` if no upper character in password
    :rtype: int
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
    """Check the username is correct

    :param user_name: The username that will be checked
    :type user_name: str
    :param function_name: The name of the function that calls this check, defaults to "check_user_input"
    :type function_name: str, optional
    :return: `0` if check succesfull, `4` if username is not a string. `5` if username is empty. `6` if username does not start with a letter
    :rtype: int
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
def check_deck_ids_input(deck_ids: list, function_name="check_deck_ids_input") -> int:
    """Check the deck_ids input if it is correct

    :param deck_ids: The deck_ids that will be checked
    :type deck_ids: list
    :param function_name: The name of the function that calls this check, defaults to "check_deck_ids_input"
    :type function_name: str, optional
    :return: `0` if check succesfull, `7` if deck_ids is empty, `8` if the list contains something diffrent than an integer
    :rtype: int
    """
    
    # check if deckid is of type list
    if not isinstance(deck_ids, list):
        log_function(MODULE_NAME, function_name, "deck_ids must be of type list", "Error")
        return 7
    # check if list is empty and if list contains elements that are not integer. If element is str but contains only a digit convert it to int
    if len(deck_ids) > 0:
        for elem in deck_ids:
            if not isinstance(elem, dict):
                log_function(MODULE_NAME, function_name, "deck_ids list must contain dictionary objects only", "Error")
                return 8
    log_function(MODULE_NAME, function_name, "Deck_Ids check was successful")
    return 0


def check_points_input(points: int, function_name = "check_points_input"):
    """Check the points input if it is correct

    :param points: The points that will be checked
    :type points: int
    :param function_name: The name of the function that calls this check, defaults to "check_points_input"
    :type function_name: str, optional
    :return: `0` if check succesfull, `9` otherwise
    :rtype: int
    """
    if not isinstance(points, int):
        log_function(MODULE_NAME, function_name, "points must be of type int", "Error")
        return 9
    if points < 0:
        log_function(MODULE_NAME, function_name, "points must be positive value", "Error")
        return 9
    log_function(MODULE_NAME, function_name, "points checked successfully", "Error")
    return 0


def get_postgress_conn(db_settings: dict):
    """Create connection to a postgress database using the given settings

    :param db_settings: settings for connection
    :type db_settings: dict
    :return: returns a connection object if connection was successful, returns None type object otherwise
    :rtype: psycopg2.connect | None
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


def create_table(conn, table_name="users") -> int:
    """Create a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param table_name: name of the table inside database, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if Creating table failed
    :rtype: int
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
                {deck_ids} JSONB,
                {points} INTEGER
            )
            """).format(
                table_name=sql.Identifier(table_name),
                user_name=sql.Identifier(TABLE_COL_NAMES[0]),
                password=sql.Identifier(TABLE_COL_NAMES[1]),
                deck_ids=sql.Identifier(TABLE_COL_NAMES[2]),
                points=sql.Identifier(TABLE_COL_NAMES[3])
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
    """Clean a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param table_name: name of the table inside database, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if Cleaning table failed
    :rtype: int
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
    """Delete a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param table_name: name of the table inside database, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if Deleting table failed
    :rtype: int
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


def add_user_with_crypt_pass(conn, user_name: str, passwd: str, deck_ids: list, table_name="users") -> int:
    """Add a new user to a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param passwd: the password of the user
    :type passwd: str
    :param deck_ids: list containing pokemon ids that resemble the deck of the user
    :type deck_ids: list[int]
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if unusual error happens, 
             `3` if user already exists,
             `4` if username is not a string, `5` if username is empty, `6` if username does not start with a letter,
             `7` if deck_ids is empty, `8` if the deck_ids list contains something diffrent that an integer,
             `10` if password not a string, `11` if password is less than 8 characters long, `12` if password does not contain digit. `13` if password does not contain an upper character.
             
    :rtype: int
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
            %s,
            %s
        )""").format(
        table_name=sql.Identifier(table_name),
        col_names=col_names
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name, passwd, json.dumps(deck_ids), 0])
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


def get_user_from_db(conn, user_name: str, table_name="users") -> UserObj:
    """Returns a user from a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: Returns empty user with id `-1` if fetch fails. Returns UserObj containing user information otherwise.
    :rtype: UserObj
    """
    
    function_name="get_user_from_db"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        f"Fetching user with name {user_name} failed. Error: Connection to DB missing.", "error")
        return UserObj.create_empty()
    
    # check input
    user_name_check = check_user_input(user_name, function_name)
    if user_name_check != 0:
        return UserObj.create_empty()
    
    try:
        log_function(MODULE_NAME, function_name, f"Trying to fetch user {user_name}")
        # create querry. get current courser of database, execute querry and commit changes
        query_base = sql.SQL("""SELECT id, {col_1}, {col_3}, {col_4} FROM {table_name} 
                             WHERE {col_1} = %s
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_2=sql.Identifier(TABLE_COL_NAMES[1]),
        col_3=sql.Identifier(TABLE_COL_NAMES[2]),
        col_4=sql.Identifier(TABLE_COL_NAMES[3])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name])
        conn.commit()
        fetch = cursor.fetchone()
        # check if the fetch was successful -> User exists or not?
        if fetch is not None:
            _id, _name, _deck_ids, _points = fetch
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} successfully")
            return UserObj(_id, _name, _deck_ids, _points)
        else:
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} not found", "warn")
            return UserObj.create_empty()
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Fetching user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return UserObj.create_empty()

def get_all_users_from_db(conn, table_name="users") -> dict:
    """Returns a dictionary containing all users in the table

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: dictionary containing all users: {"users": list(UserObj)}
    :rtype: dict
    """
    function_name="get_all_users_from_db"

    # check connection
    if conn is None:
        log_function(MODULE_NAME, function_name, 
        "Fetching users failed. Error: Connection to DB missing.", "error")
        return {}
    
    try:
        log_function(MODULE_NAME, function_name, "Trying to fetch all users")
        # create querry. get current courser of database, execute querry and commit changes
        query_base = sql.SQL("""SELECT id, {col_1}, {col_3}, {col_4} FROM {table_name}""").format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_3=sql.Identifier(TABLE_COL_NAMES[2]),
        col_4=sql.Identifier(TABLE_COL_NAMES[3])
        )

        cursor = conn.cursor()
        cursor.execute(query_base)
        conn.commit()
        fetch = cursor.fetchall()
        
        # check if the fetch was successful -> User exists or not?
        if fetch is not None:
            user_arry = []
            for elem in fetch:
                _id, _name, _deck_ids, _points = elem
                user_arry.append(UserObj(_id, _name, _deck_ids, _points).__dict__())
            return {"users": user_arry}
        else:
            log_function(MODULE_NAME, function_name, "Table empty", "warn")
            return {"users": []}
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Fetching users failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return {}

def authenticate_user_from_db(conn, user_name: str, user_password: str, table_name="users") -> UserObj:
    """Returns a user from a table inside the database if password is correct

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param user_password: the password of the user
    :type user_password: str
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: Returns empty user with id `-1` if fetch fails. Returns UserObj containing user information otherwise.
    :rtype: UserObj
    """
    
    function_name="authenticate_user_from_db"

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
        query_base = sql.SQL("""SELECT id, {col_1}, {col_3}, {col_4} FROM {table_name} 
                             WHERE {col_1} = %s
                             AND {col_2} = crypt(%s, password);
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_2=sql.Identifier(TABLE_COL_NAMES[1]),
        col_3=sql.Identifier(TABLE_COL_NAMES[2]),
        col_4=sql.Identifier(TABLE_COL_NAMES[3])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [user_name, user_password])
        conn.commit()
        fetch = cursor.fetchone()
        # check if the fetch was successful -> User exists or not?
        if fetch is not None:
            _id, _name, _deck_ids, _points = fetch
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} successfully")
            return UserObj(_id, _name, _deck_ids, _points)
        else:
            log_function(MODULE_NAME, function_name, f"Fetched user {user_name} not found", "warn")
            return UserObj.create_empty()
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Fetching user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return UserObj.create_empty()


def update_user_from_db(conn, user_name: str, deck_ids: list, table_name="users") -> int:
    """Update a user from a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param deck_ids: list containing pokemon ids that resemble the deck of the user
    :type deck_ids: list[int]
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if unusual error happens, 
             `4` if username is not a string, `5` if username is empty, `6` if username does not start with a letter,
             `7` if deck_ids is empty, `8` if the deck_ids list contains something diffrent that an integer
    :rtype: int
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
        cursor.execute(query_base, [json.dumps(deck_ids), user_name])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Updated user {user_name} successfully")
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Updating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return 2

def update_user_from_db_points(conn, user_name: str, points: int, table_name="users") -> int:
    """Update a user from a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param points: points of the user that should be updated
    :type points: int
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if unusual error happens, 
             `4` if username is not a string, `5` if username is empty, `6` if username does not start with a letter,
             `9` if points are negative or not integer
    :rtype: int
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
    
    points_check = check_points_input(points, function_name)
    if points_check != 0:
        return points_check

    try:
        log_function(MODULE_NAME, function_name, f"Trying to update user {user_name}")
        # create querry. get current courser of database, execute querry and commit changes
        query_base = sql.SQL("""UPDATE {table_name} 
                             SET {col_4} = %s 
                             WHERE {col_1} = %s
                             """).format(
        table_name=sql.Identifier(table_name),
        col_1=sql.Identifier(TABLE_COL_NAMES[0]),
        col_4=sql.Identifier(TABLE_COL_NAMES[3])
        )

        cursor = conn.cursor()
        cursor.execute(query_base, [points, user_name])
        conn.commit()
        log_function(MODULE_NAME, function_name, f"Updated user {user_name} successfully")
        return 0
    except ps.Error as e:
        log_function(MODULE_NAME, function_name, f"Updating user {user_name} failed. Error: {type(e)} | {e.__str__()}", "error")
        conn.rollback()
        return 2


def delete_user_from_db(conn, user_name: str, table_name="users"):
    """Delete a user from a table inside the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :param user_name: the name of the user
    :type user_name: str
    :param table_name: Name of the table, defaults to "users"
    :type table_name: str, optional
    :return: `0` if successful, `1` if None Type connection, `2` if unusual error happens, 
             `4` if username is not a string, `5` if username is empty, `6` if username does not start with a letter
    :rtype: int
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
    """Close the connection to the database

    :param conn: Connection object must not be None type
    :type conn: psycopg2.connect
    :return: `0` if successful, `1` if None Type connection, `2` if unusual error happens
    :rtype: int
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