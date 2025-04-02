from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager


def reset_caches(towns_profile: TownsProfileManager):
    try:
        # find and click bug_report button
        bug_report_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='report-bug-button']")))
        bug_report_element.click()

        # find and click reset_caches button
        reset_caches_elements = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Reset Caches')]")))
        reset_caches_elements.click()

        # find and click confirm reset caches button
        confirm_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Confirm')]")))
        confirm_element.click()

        logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully RESETED CACHES!")

    except Exception as e:
        logger.error(f"Profile_id: {towns_profile.profile_id}. {e}")
