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