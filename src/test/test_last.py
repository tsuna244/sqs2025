from fastapi.testclient import TestClient

from api.modules.interface import PokemonRarity

import pytest
import json

import psycopg2 as ps

import os

# set test environment before loading api!!!
os.environ["TEST"] = "1"

print("test")

import api

client = TestClient(api.app)

## Last Testing
def test_last_test(mocker):
    def __init__(self, poke_id):
        if poke_id < 1:
            log.error("Pokemon Id must be greater than 1")
            raise ValueError("Pokemon Id must be greater than 1")

        self._poke_id = poke_id

        self._name = "test_ditto"
        self._generation = 1
        self._rarity = PokemonRarity.NORMAL
        self._points = 0
        self._stats = []
        self._sprite = ""

    mocker.patch.object(api.modules.interface.PokemonObj, '__init__', __init__)
    response = client.post("/Pokemon_Id/132")
    assert json.loads(response.content)["pokemon_name"] == "test_ditto"
