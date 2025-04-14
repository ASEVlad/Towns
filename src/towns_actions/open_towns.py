import time
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error


def open_towns(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. OPEN TOWNs action just have started!")

        # Open a new tab/window using Selenium’s built-in method
        towns_profile.driver.switch_to.new_window('tab')

        # open main page
        towns_profile.driver.get("https://app.towns.com/explore")
        towns_profile.driver.implicitly_wait(5)

        if "Towns" in towns_profile.driver.title:
            # wait till open
            element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='/t/new'] | //*[contains(text(), 'Log In')]")))

            time.sleep(2)

            # return True if Login is needed
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully OPENED main page!")
            return element.text == "Log In"
        else:
            raise "Could not open main page"

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise
