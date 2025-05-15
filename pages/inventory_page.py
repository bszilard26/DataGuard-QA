# pages/inventory_page.py

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class InventoryPage(BasePage):
    PAGE_TITLE = (By.CLASS_NAME, "title")
    FIRST_ITEM = (By.CLASS_NAME, "inventory_item")
    CART_BUTTON = (By.CLASS_NAME, "shopping_cart_link")

    def is_loaded(self):
        return self.get_element_text(self.PAGE_TITLE) == "Products"

    def first_item_is_visible(self):
        return self.driver.find_element(*self.FIRST_ITEM).is_displayed()

    def go_to_cart(self):
        self.driver.find_element(*self.CART_BUTTON).click()
