from locust import HttpUser, between, task
import os

from api.modules.module_postgresql import *

# set env var TEST to 2 for stress testing (1 is for unit test !!!)
os.environ['TEST'] = '2'

class WebsiteUser(HttpUser):
    wait_time = between(5, 15)
    
    def on_start(self):
        self.client.post("/token", data={"username":"testuser", "password":"Asdf1234"})
    
    # ===== PAGES =====

    @task
    def index(self):
        self.client.get("/")

    @task
    def leaderboard(self):
        self.client.get("/leaderboard")

    @task 
    def deck(self):
        self.client.get("/my_deck")

    @task
    def unauth(self):
        self.client.get("/unauth")

    @task
    def pack(self):
        self.client.get("/pack_opening")

    # ===== POKEMON =====

    @task
    def get_pokemon(self):
        self.client.post("/Pokemon_Id/1")

    @task
    def get_pokemon_by_name(self):
        self.client.post("/Pokemon_Name/ditto")

    @task
    def get_pokemon_rand(self):
        self.client.post("/Pokemon_Rand/2")    

    # ===== USER =====

    @task
    def users(self):
        self.client.post("/get_users")
    
    @task
    def add_to_deck(self):
        self.client.post("/add_to_deck", json={"username":"testuser", "new_elem":{"_id": 132, "_name": "ditto"}})

    @task
    def update_points(self):
        self.client.post("/update_points", json={"username":"testuser", "points_elem":244})

    # ===== 
    # cmd locust -f test/locust_stress_test.py --host http://127.0.0.1:8000 -t 30s -u 5 --headless