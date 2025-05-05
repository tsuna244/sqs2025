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

@pytest.fixture(scope='session')
def db_connection():
    """
    :param docker_services: pytest-docker plugin fixture
    :param docker_ip: pytest-docker plugin fixture
    :return: psycopg2 connection class
    """
    db_settings = {
        'database'        : 'test_database',
        'user'            : 'postgres',
        'host'            : host,
        'password'        : 'test_passwd',
        'port'            : 5432
    }
    conn = get_postgress_conn(db_settings)
    conn.autocommit = True
    return conn

def test_create_table(db_connection):
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
    # add user successfully
    assert add_user_with_crypt_pass(db_connection, "test_user", "123456AB", []) == 0