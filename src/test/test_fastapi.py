from fastapi.testclient import TestClient

import os
import testcontainers.compose

# start the docker containers, based on tests/mocks/docker-compose.yml file
container = testcontainers.compose.DockerCompose(os.path.abspath("tests/"))
if len(container.get_containers()) != 1:
    container.start()

host = f'{container.get_service_host("database", 5432)}'
test_table = "test_table"

db_settings = {
        'database'        : 'test_database',
        'user'            : 'postgres',
        'host'            : host,
        'password'        : 'test_passwd',
        'port'            : 5432
    }

# set test environment before loading api!!!
os.environ["TEST"] = "1"

import api

api.db = api.create_db(db_settings)

client = TestClient(api.app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Test": "Test"}