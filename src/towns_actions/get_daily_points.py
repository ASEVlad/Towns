import time
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import get_full_xpath_element


def get_daily_points(towns_profile: TownsProfileManager):
    try:
        # check if the tab is already opened
        els = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Towns Points')]")
        if len(els) == 0:
            # click on beaver icon
            towns_points_element = towns_profile.driver.find_element("xpath", '//img[@alt="Towns Points"]')
            towns_points_element.click()

        # find element inside beaver box
        beaver_text_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Towns Points')]")))

        # find beaver_box element
        beaver_text_xpath = get_full_xpath_element(towns_profile.driver, beaver_text_element)
        beaver_box_xpath = beaver_text_xpath[:beaver_text_xpath.rfind("div[") - 1]
        WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, beaver_box_xpath)))

        # find and click on beaver_belly element
        beaver_belly_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//canvas")))
        beaver_belly_element = beaver_belly_element.find_element("xpath", "..").find_element("xpath", ".//span")
        beaver_belly_element.click()
        time.sleep(2)

        # check on cooldown
        cooldown_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'The beaver is not ready for his belly rub')]")
        if len(cooldown_elements) == 0:
            # find and click on pay_with_ETH button
            pay_with_ETH_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Pay with ETH')]")))
            pay_with_ETH_element.click()

            # wait untill the tx will be processed
            text_to_wait = "You've earned"
            WebDriverWait(towns_profile.driver, 40).until(EC.visibility_of_element_located((By.XPATH, f'//*[contains(text(), "{text_to_wait}")]')))
            logger.info(f"Profile_id: {towns_profile.profile_id}. Daily points are successfully farmed!")

        else:
            logger.info(f"Profile_id: {towns_profile.profile_id}. Cooldown for daily points!")

    except Exception as e:
        logger.error(f"Profile_id: {towns_profile.profile_id}. {e}")

