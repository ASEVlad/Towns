from loguru import logger
from selenium.webdriver.common.by import By

from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error, wait_until_element_is_visible


def update_towns(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. UPDATE TOWNs action just have started!")

        # try to find element with text 'Update Towns'
        update_towns_p_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Update Towns')]")

        # if element exists
        if len(update_towns_p_elements):
            button_elements = towns_profile.driver.find_elements(By.XPATH, "//button")
            for button_element in button_elements:
                try:
                    p_elements = button_element.find_elements(By.TAG_NAME, "p")
                    if len(p_elements) == 1:
                        p_element = p_elements[0]
                        if "Update Towns" in p_element.text:
                            button_element.click()

                            # wait till Send_message element is loaded
                            wait_until_element_is_visible(
                                towns_profile,
                                By.XPATH,
                                "//*[@data-testid='send-message-text-box']"
                            )

                            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully UPDATED town!")
                except:
                    pass
        else:
            logger.info("No element 'Update Towns'")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
