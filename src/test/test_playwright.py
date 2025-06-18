import re
from playwright.sync_api import Page, expect

import os
import testcontainers.compose

# start the docker containers, based on tests/mocks/docker-compose.yml file
container = testcontainers.compose.DockerCompose(os.path.abspath("tests_playwright/"))
if len(container.get_containers()) != 1:
    container.start()

host = f'{container.get_service_host("api", 80)}'

base_url = "http://" + host + ":80"

def test_has_title(page: Page):
    page.goto(base_url + "/")
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Sqs2025"))

def test_get_navbar(page: Page):
    page.goto(base_url + "/")

    page.get_by_role("link", name="Packopening").click()
    expect(page).to_have_url(base_url + "/#")
    page.get_by_role("link", name="My-Deck").click()
    expect(page).to_have_url(base_url + "/#")

    # Click the get started link.
    page.get_by_role("link", name="Leaderboard").click()
    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Leaderboard")).to_be_visible()

def test_search_bar(page: Page):

    page.goto(base_url + "/")
    # fail
    page.get_by_role("searchbox", name="Search").fill("test")
    print(page.get_by_role("searchbox", name="Search").input_value())
    page.get_by_role("button", name="Search").click()
    
    expect(page.locator("#loading")).to_contain_text("Pokemon not found!")
    # success
    page.goto(base_url + "/")
    page.get_by_role("searchbox", name="Search").fill("ditto")
    page.get_by_role("button", name="Search").click()
    expect(page.locator("#poke_elem")).to_contain_text("Pokemon Id:")


def test_register_user(page: Page):
    page.goto(base_url + "/")
    # press register button
    page.get_by_role("button", name="Register", exact=True).click()
    # test user with 
    page.get_by_role("textbox", name="Username").fill("test_user")
    # insert Password alpha only with lower only
    page.get_by_role("textbox", name="Password", exact=True).fill("aasd")
    expect(page.locator("#letter")).to_have_class("bi mr-1 bi-check-lg text-success")
    # check for length
    page.get_by_role("textbox", name="Password", exact=True).fill("aasdfasdf")
    expect(page.locator("#length")).to_have_class("bi mr-2 bi-check-lg text-success")
    # check for capital
    page.get_by_role("textbox", name="Password", exact=True).fill("Aasdfasdf")
    expect(page.locator("#capital")).to_have_class("bi mr-1 bi-check-lg text-success")
    # check for number
    page.get_by_role("textbox", name="Password", exact=True).fill("Asdf1234")
    expect(page.locator("#number")).to_have_class("bi mr-2 bi-check-lg text-success")

    # test repeat password wrong
    page.get_by_role("textbox", name="Repeat password").fill("wrongpswd")
    expect(page.get_by_text("Does not equal password")).to_be_visible()
    # test correct password
    page.get_by_role("textbox", name="Repeat password").fill("Asdf1234")
    expect(page.get_by_text("Same password")).to_be_visible()

    # test register button with bad username (contains _)
    page.get_by_role("button", name=" Register").click()
    expect(page.get_by_role("heading", name="Input error! Username must be")).to_be_visible()
    page.get_by_text("Home Leaderboard Packopening My-Deck Login Register Register with username and").press("Escape")

    # successfull register
    page.goto(base_url + "/register")

    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("textbox", name="Password", exact=True).fill("Asdf1234")
    page.get_by_role("textbox", name="Repeat password").fill("Asdf1234")
    page.get_by_role("button", name=" Register").click()
    
    expect(page).to_have_url(base_url + "/login")
    expect(page.get_by_text("Login with username and")).to_be_visible()

def test_login(page: Page):
    # no password
    page.goto(base_url + "/login")
    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("button", name=" Login").click()
    expect(page.locator("#modalMessage")).to_contain_text("Username or Password wrong")
    # wrong password
    page.goto(base_url + "/login")
    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("textbox", name="Password").fill("wrongpswd")
    page.get_by_role("button", name=" Login").click()
    expect(page.locator("#modalMessage")).to_contain_text("Username or Password wrong")
    # successfull login
    page.goto(base_url + "/login")
    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("textbox", name="Password").fill("Asdf1234")
    page.get_by_role("button", name=" Login").click()
    expect(page.locator("#login_register")).to_contain_text("testuser")

def test_deck_page_and_logout(page):

    # login
    page.goto(base_url + "/login")
    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("textbox", name="Password").fill("Asdf1234")
    page.get_by_role("button", name=" Login").click()

    page.get_by_role("link", name="My-Deck").click()
    expect(page.get_by_role("heading")).to_contain_text("My_Deck")

    # test logout
    page.get_by_role("button", name="Logout").click()
    expect(page.get_by_role("button", name="Login")).to_be_visible()

def test_get_pokemon(page: Page):
    
    # login
    page.goto(base_url + "/login")
    page.get_by_role("textbox", name="Username").fill("testuser")
    page.get_by_role("textbox", name="Password").fill("Asdf1234")
    page.get_by_role("button", name=" Login").click()

    page.get_by_role("link", name="Packopening").click()
    expect(page.get_by_role("heading")).to_contain_text("Packopening:")