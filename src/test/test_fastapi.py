from fastapi.testclient import TestClient

import pytest
import json

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

client = TestClient(api.app)

def test_create_db():
    api.create_db(db_settings)
    assert True

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

# test /register page and /register_user
def test_register_user():
    # register webpage response
    response = client.get("/register")
    assert response.status_code == 200
    # register function with wrong username (alpha only)
    response = client.post("register_user",
        headers={'Content-Type': 'application/json'},
        json={"username": "test_user", "password": "Asdf1234"}
        )
    assert response.content == b'{"details":"Input error! Username must be alpha only"}'
    # register funciton with wrong password type (asscii only)
    response = client.post("register_user",
        headers={'Content-Type': 'application/json'},
        json={"username": "testuser", "password": "Asdf§1234"}
        )
    assert response.content == b'{"details":"Input error! Password must be ascii chars only"}'
    # register user successfully
    response = client.post("register_user",
        headers={'Content-Type': 'application/json'},
        json={"username": "testuser", "password": "Asdf1234"}
        )
    assert response.content == b'{"details":"User testuser successfully registered"}'
    # register user that alreay exists
    response = client.post("register_user",
        headers={'Content-Type': 'application/json'},
        json={"username": "testuser", "password": "Asdf1234"}
        )
    assert response.content == b'{"details":"UnuiqeViolation! User testuser already exists"}'

# test /token and /get_user
def test_token():
    # receive token
    response = client.post("/token", data={'username': "testuser", 'password': "Asdf1234"})
    token = response.content
    assert response.status_code == 200
    # get user with token
    current_token = json.loads(token)
    headers = {'Authorization': current_token["token_type"] + " " + current_token["access_token"] }
    response = client.post("/get_user", headers=headers)
    assert json.loads(response.content)["user_name"] == "testuser"
    # get user not authentikatet
    response = client.post("/get_user")
    print(response.content)
    assert response.content == b'{"detail":"Not authenticated"}'

def test_get_users():
    response = client.post("/get_users")
    assert len(json.loads(response.content)["users"]) == 1

def test_pages():
    response = client.get("/leaderboard")
    assert response.status_code == 200

    response = client.get("/my_deck")
    assert response.status_code == 200

    response = client.get("/pack_opening")
    assert response.status_code == 200

    response = client.get("/unauth")
    assert response.status_code == 200

    response = client.get("/login")
    assert response.status_code == 200

def test_get_pokemon():
    response = client.post("/Pokemon_Id/132")
    print(response.content)
    assert json.loads(response.content)["pokemon_name"] == "ditto"

    response = client.post("/Pokemon_Name/ditto")
    print(response.content)
    assert json.loads(response.content)["pokemon_name"] == "ditto"

def test_rand_pokemon():
    # wrong generation
    response = client.post("/Pokemon_Rand/7")
    assert response.status_code == 404

    # gen 1
    response = client.post("/Pokemon_Rand/1")
    assert json.loads(response.content)["pokemon_generation"] == "generation-i"

    response = client.post("/Pokemon_Rand/2")
    assert json.loads(response.content)["pokemon_generation"] == "generation-ii"

    response = client.post("/Pokemon_Rand/3")
    assert json.loads(response.content)["pokemon_generation"] == "generation-iii"

def test_update_user():
    json_header = {'Content-Type': 'application/json'}
    # fail due to wrong username
    response = client.post("/add_to_deck", headers=json_header, json={"username": "test_user", "new_elem": {"_id": "132", "_name": "ditto"}})
    assert response.content == b'{"details":"Input error! Username must be alpha only"}'
    # add successfully
    response = client.post("/add_to_deck", headers=json_header, json={"username": "testuser", "new_elem": {"_id": "132", "_name": "ditto"}})
    assert response.content == b'{"details":"New element got added to user"}'
    
    # same for points
    response = client.post("/update_points", headers=json_header, json={"username": "test_user", "points_elem": 10})
    assert response.content == b'{"details":"Input error! Username must be alpha only"}'
    # fail due to negative value
    response = client.post("/update_points", headers=json_header, json={"username": "testuser", "points_elem": -1})
    assert response.content == b'{"details":"Input error! Point elem must be positive integer"}'
    # success
    response = client.post("/update_points", headers=json_header, json={"username": "testuser", "points_elem": 10})
    assert response.content == b'{"details":"Added points to user successfully"}'

    
def test_stop_db():
    api.close_db()
    assert True