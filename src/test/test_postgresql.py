from api.modules.module_postgresql import *

import pytest
import os
import pytest
import testcontainers.compose

# start the docker containers, based on tests/mocks/docker-compose.yml file
container = testcontainers.compose.DockerCompose(os.path.abspath("tests/"))
if len(container.get_containers()) != 1:
    container.start()

# get the host of postgresql container
host = f'{container.get_service_host("database", 5432)}'
test_table = "test_table"

def db_connection():
    db_settings = {
        'database'        : 'test_database',
        'user'            : 'postgres',
        'host'            : host,
        'password'        : 'test_passwd',
        'port'            : 5432
    }
    conn = get_postgress_conn(db_settings)
    conn.autocommit = True
    base_query = "DROP TABLE IF EXISTS users"
    cur = conn.cursor()
    cur.execute(base_query)
    conn.commit()
    return conn

db_connection = db_connection()

# unit test for check functions
def test_check_user_input():
    assert check_user_input(123) == 4
    assert check_user_input("") == 5
    assert check_user_input("1test") == 6
    assert check_user_input("_test") == 6


def test_check_passwd_input():
    assert check_passwd_input(123) == 10
    assert check_passwd_input("") == 11
    assert check_passwd_input("abcdabcd") == 12
    assert check_passwd_input("1234abcd") == 13
    assert check_passwd_input("1234AbCd") == 0


def test_check_deck_ids_input():
    assert check_deck_ids_input(123) == 7
    assert check_deck_ids_input("") == 7
    assert check_deck_ids_input([]) == 0
    assert check_deck_ids_input([1, "abc"]) == 8
    deck_ids = [{"_id": 1, "_name": "name"}, {"_id": 2, "_name": "name_two"}]
    assert check_deck_ids_input(deck_ids) == 0


def test_user_object():
    empty_obj = UserObj.create_empty()
    assert empty_obj.user_id == -1
    assert empty_obj.user_name == ""
    assert empty_obj.deck_ids == []
    assert empty_obj.__empty__() == True
    not_empty_obj = UserObj(1, "test_name", [{"_id": 1, "_name": "name"}])
    assert not_empty_obj.__eq__(UserObj(1, "test_name", [{"_id": 1, "_name": "name"}])) == True
    test_dict = {"user_id": 1, "user_name": "test_name", "deck_ids": [{"_id": 1, "_name": "name"}]}
    assert not_empty_obj.__dict__() == test_dict
    assert not_empty_obj.__str__() == test_dict.__str__()


# integration with db
def test_create_table():
    # create table with none type connection
    assert create_table(None) == 1
    assert create_table(db_connection) == 0
    # create table again (should return true since IF NOT EXISTS checks internally)
    assert create_table(db_connection) == 0

def test_add_user():
    # add user with none type connection
    assert add_user_with_crypt_pass(None, "", "", []) == 1
    # add user with wrong password
    assert add_user_with_crypt_pass(db_connection, "test_user", 1234, []) == 10
    # add user without user name
    assert add_user_with_crypt_pass(db_connection, 123, "1234ABCD", []) == 4
    # add user with bad deck_ids list
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", "") == 7
    # add user successfully
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", [{"_id": 1, "_name": "name"}]) == 0
    # add same user again
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", []) == 3


def test_update_user():
    # update user with none type connection
    assert update_user_from_db(None, "", []) == 1
    # update user with wrong name input
    assert update_user_from_db(db_connection, 123, []) == 4
    # update user with bad deck_ids list
    assert update_user_from_db(db_connection, "test_user", "") == 7
    # update user successfully
    assert update_user_from_db(db_connection, "test_user", [{"_id": 1, "_name": "name"}, {"_id": 2, "_name": "name2"}]) == 0
    

def test_get_user_from_db():
    # get user with none type connection
    assert get_user_from_db(None, "").__eq__(UserObj.create_empty())
    # get user with wrong username type
    assert get_user_from_db(db_connection, 123).__eq__(UserObj.create_empty())
    # get non existing user
    assert get_user_from_db(db_connection, "idontexist").__eq__(UserObj.create_empty())
    # get user successfully
    print(get_user_from_db(db_connection, "test_user"))
    assert get_user_from_db(db_connection, "test_user").__eq__(UserObj(2, "test_user", [{"_id": 1, "_name": "name"}, {"_id": 2, "_name": "name2"}]))

def test_authenticate_user_from_db():
    # authenticate user with none type connection
    assert authenticate_user_from_db(None, "", "").__eq__(UserObj.create_empty())
    # authenticate user with wrong name type
    assert authenticate_user_from_db(db_connection, 123, "123456AB")
    # authenticate user with wrong password type
    assert authenticate_user_from_db(db_connection, "test_user", 123)
    # test non existing user
    assert authenticate_user_from_db(db_connection, "nonexistinguser", "1234AbCd").__empty__()
    # authenticate user successfully
    print(authenticate_user_from_db(db_connection, "test_user", "123456AB"))
    assert authenticate_user_from_db(db_connection, "test_user", "123456AB").__eq__(UserObj(2, "test_user", [{"_id": 1, "_name": "name"}, {"_id": 2, "_name": "name2"}]))

def test_delete_user():
    # delete user with none type connection
    assert delete_user_from_db(None, "") == 1
    # delete user with wrong user input
    assert delete_user_from_db(db_connection, 123) == 4
    # delete user succesfully
    assert delete_user_from_db(db_connection, "test_user") == 0


def test_clean_table():
    assert clean_table(None) == 1
    assert clean_table(db_connection, table_name="not_existing") == 2
    assert clean_table(db_connection) == 0

def test_get_all_users_from_db():
    # get users with none type connection
    assert get_all_users_from_db(None) == {}
    # get users from empty table
    assert get_all_users_from_db(db_connection) == {"users": []}
    add_user_with_crypt_pass(db_connection, "test_user_second", "1234ABcd", [{"_id": 1, "_name": "name"}, {"_id": 2, "_name": "name2"}])
    assert len(get_all_users_from_db(db_connection)["users"]) == 1

def test_delete_table():
    assert delete_table(None) == 1
    assert delete_table(db_connection, table_name="not_existing") == 0
    assert delete_table(db_connection) == 0


def test_close_connection():
    assert close_connection(None) == 1
    assert close_connection(db_connection) == 0