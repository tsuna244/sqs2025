from fastapi.testclient import TestClient

import api

client = TestClient(api.app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Test": "Test"}