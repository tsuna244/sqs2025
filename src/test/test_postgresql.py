from api.modules.module_postgresql import *

import pytest
import os
import pytest
import testcontainers.compose

# start the docker containers, based on tests/mocks/docker-compose.yml file
container = testcontainers.compose.DockerCompose(os.path.abspath("tests/"))
container.start()

# get the host of postgresql container
host = f'{container.get_service_host("database", 5432)}'
test_table = "test_table"

@pytest.fixture(scope='session')
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

def test_create_table(db_connection):
    # create table with none type connection
    assert create_table(None) == False
    assert create_table(db_connection) == True
    # create table again (should return true since IF NOT EXISTS checks internally)
    assert create_table(db_connection) == True

def test_add_user(db_connection):
    # add user with none type connection
    assert add_user_with_crypt_pass(None, "", "", []) == 1
    # add user with wrong password
    assert add_user_with_crypt_pass(db_connection, "test_user", 1234, []) == 10 # pwd is not str
    assert add_user_with_crypt_pass(db_connection, "test_user", "", []) == 11 # pwd must be longer than 7
    assert add_user_with_crypt_pass(db_connection, "test_user", "abcdabcd", []) == 12 # pwd must contain digits
    assert add_user_with_crypt_pass(db_connection, "test_user", "1234abcd", []) == 13 # pwd must contain upper char
    # add user without user name
    assert add_user_with_crypt_pass(db_connection, 123, "1234ABCD", []) == 4
    assert add_user_with_crypt_pass(db_connection, "", "1234ABCD", []) == 5
    assert add_user_with_crypt_pass(db_connection, "_test", "1234ABCD", []) == 6
    assert add_user_with_crypt_pass(db_connection, "1test", "1234ABCD", []) == 6
    # add user with bad deck_ids list
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", "") == 7
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", ["abc"]) == 8
    # add user successfully
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", [1, "1"]) == 0
    # add same user again
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", []) == 3


def test_update_user(db_connection):
    # update user with none type connection
    assert update_user_from_db(None, "", []) == 1
    # update user with wrong name input
    assert update_user_from_db(db_connection, 123, []) == 4
    assert update_user_from_db(db_connection, "", []) == 5
    assert update_user_from_db(db_connection, "_test", []) == 6
    assert update_user_from_db(db_connection, "1test", []) == 6
    # update user with bad deck_ids list
    assert update_user_from_db(db_connection, "test_user", "") == 7
    assert update_user_from_db(db_connection, "test_user", [2, "abc", 1]) == 8
    # update user successfully
    assert update_user_from_db(db_connection, "test_user", [1, "2", 3]) == 0
    

def test_get_user_from_db(db_connection):
    # get user with none type connection
    assert get_user_from_db(None, "", "").__eq__(UserObj.create_empty())
    # get user with wrong password
    assert get_user_from_db(db_connection, "test_user", 1234).__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "test_user", "").__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "test_user", "abcdabcd").__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "test_user", "1234abcd").__eq__(UserObj.create_empty())
    # get user with wrong username
    assert get_user_from_db(db_connection, 123, "123456AB").__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "", "123456AB").__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "_test", "123456AB").__eq__(UserObj.create_empty())
    assert get_user_from_db(db_connection, "1test", "123456AB").__eq__(UserObj.create_empty())
    # get user successfully
    print(get_user_from_db(db_connection, "test_user", "123456AB"))
    assert get_user_from_db(db_connection, "test_user", "123456AB").__eq__(UserObj(1, "test_user", [1, 2, 3]))

