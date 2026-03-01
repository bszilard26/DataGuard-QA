# pages/base_page.py

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def click(self, by_locator):
        WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable(by_locator)).click()

    def enter_text(self, by_locator, text):
        WebDriverWait(self.driver, 10).until(
            ec.visibility_of_element_located(by_locator)
        ).send_keys(text)

    def get_title(self):
        return self.driver.title

    def get_element_text(self, by_locator):
        return (
            WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(by_locator)).text
        )
