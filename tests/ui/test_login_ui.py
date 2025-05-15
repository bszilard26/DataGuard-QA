import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from pages.login_page import LoginPage

@pytest.mark.skipif("CI" in os.environ, reason="Skip UI test in Docker/CI")
def test_login_swag_labs():
    options = Options()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    login_page = LoginPage(driver)
    login_page.load()
    login_page.login("standard_user", "secret_sauce")

    assert "inventory" in driver.current_url
    time.sleep(2)
    driver.quit()
