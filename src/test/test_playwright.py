import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("http://127.0.0.1:8000/")
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Sqs2025"))

def test_get_started_link(page: Page):
    page.goto("http://127.0.0.1:8000/")

    # Click the get started link.
    page.get_by_role("link", name="Leaderboard").click()
    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Leaderboard")).to_be_visible()