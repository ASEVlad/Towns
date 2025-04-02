import time
import random
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import get_full_xpath_element


def open_random_town(towns_profile: TownsProfileManager):
    try:
        # open main page
        towns_profile.driver.get("https://app.towns.com/explore")

        # find create_new_town element
        new_town_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//a[@href="/t/new"]')))
        new_town_xpath = get_full_xpath_element(towns_profile.driver, new_town_element)
        time.sleep(2)

        # find left_box element
        left_box_xpath = new_town_xpath[:new_town_xpath.rfind("div[") - 1]
        left_box_element = towns_profile.driver.find_element("xpath", left_box_xpath)

        # find all left_box elements
        left_box_elements = left_box_element.find_elements("xpath", "./div")
        towns_num = len(left_box_elements) - 2

        if towns_num != 0:
            # choose random towns
            town_to_open = random.randint(0, towns_num - 1)

            # open random towns
            left_box_elements[town_to_open + 2].click()
            WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully OPENED random town!")
            return towns_profile.driver.current_url
        else:
            logger.info(f"Profile_id: {towns_profile.profile_id}. No Towns to open!")
            return None

    except Exception as e:
        logger.error(f"Profile_id: {towns_profile.profile_id}. {e}")
        return None
