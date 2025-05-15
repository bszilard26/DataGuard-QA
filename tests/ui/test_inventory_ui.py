# tests/ui/test_inventory_ui.py

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

@pytest.mark.skipif("CI" in os.environ, reason="Skip UI test in Docker/CI")
def test_inventory_page_load():
    options = Options()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Login
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login("standard_user", "secret_sauce")

    # Inventory Page
    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded()
    assert inventory_page.first_item_is_visible()

    time.sleep(2)
    driver.quit()
