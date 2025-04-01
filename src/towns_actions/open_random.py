import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import get_full_xpath_element


def open_random_town(towns_profile: TownsProfileManager):
    # find create_new_town element
    new_town_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//a[@href="/t/new"]')))
    new_town_xpath = get_full_xpath_element(towns_profile.driver, new_town_element)

    # find left_box element
    left_box_xpath = new_town_xpath[:new_town_xpath.rfind("div[") - 1]
    left_box_element = towns_profile.driver.find_element("xpath", left_box_xpath)

    # find all left_box elements
    left_box_elements = left_box_element.find_elements("xpath", "./div")
    towns_num = len(left_box_elements) - 2

    # choose random towns
    town_to_open = random.randint(0, towns_num - 1)

    # open random towns
    left_box_elements[town_to_open + 2].click()
    WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))
