from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error


def reset_caches(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. RESET CACHES action just have started!")

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
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
