from fastapi.testclient import TestClient

import api

db_settings = {
        'database'        : 'test_database',
        'user'            : 'postgres',
        'host'            : host,
        'password'        : 'test_passwd',
        'port'            : 5432
    }

api.db = api.create_db(db_settings)

client = TestClient(api.app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Test": "Test"}