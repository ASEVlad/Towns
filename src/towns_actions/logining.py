from loguru import logger
from selenium.webdriver.common.by import By

from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error, wait_until_element_is_visible


def login_twitter(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. LOGIN WITH TWITTER action just have started!")

        # find element with Login text
        login_button_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//button[contains(text(), 'Log In')]")
        # click Login button
        login_button_element.click()

        # wait until elements are loaded
        wait_until_element_is_visible(towns_profile, By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # find login_method elements
        login_elements = towns_profile.driver.find_elements(By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # get twitter method_element
        twitter_method_element = find_login_method_element(login_elements, "Twitter")
        # click
        twitter_method_element.click()

        # find authorize button
        autorize_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//button[@data-testid='OAuth_Consent_Button']")
        # click
        autorize_element.click()

        # wait until successfull text will appear
        success_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Successfully connected with Twitter')] | //*[contains(text(), 'Authentication failed')]"
        )

        if success_element.text == "Authentication failed":
            error = success_element.find_element(By.XPATH, "..").text
            logger.error(f"Profile_id: {towns_profile.profile_id}. {error}")
            raise error
        else:
            towns_profile.linked_accounts.add("TWITTER")
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully LOGINED in TWITTER!")
            return True

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def login_google(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. LOGIN WITH GOOGLE action just have started!")

        # find element with Login text
        login_button_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//button[contains(text(), 'Log In')]")
        # click Login button
        login_button_element.click()

        # wait till elements are visible
        wait_until_element_is_visible(towns_profile, By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # find login_method elements
        login_elements = towns_profile.driver.find_elements(By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # get and click twitter method_element
        google_method_element = find_login_method_element(login_elements, "Google")
        google_method_element.click()

        # find and click first google account
        login_elements = wait_until_element_is_visible(towns_profile, By.XPATH, "//*[@role='link' and @data-item-index='0']")
        login_elements.click()

        # wait until successfull text will appear
        success_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Successfully connected with Google')] | //*[contains(text(), 'Authentication failed')]"
        )

        if success_element.text == "Authentication failed":
            print(success_element.find_element(By.XPATH, "..").text)
            return False
        else:
            towns_profile.linked_accounts.add("GOOGLE")
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully LOGINED in GOOGLE!")
            return True

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def check_reauthentication(towns_profile: TownsProfileManager):
    try:
        towns_profile.driver.get("https://app.towns.com/t/new")

        check_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Please reauthenticate')] | //*[contains(text(), 'Next')]"
        )

        if "Please reauthenticate" in check_element.text:
            logger.info(f"Profile_id: {towns_profile.profile_id}. There is a need in REAUTHENTICATION")
            return True
        else:
            logger.info(f"Profile_id: {towns_profile.profile_id}. There is NO need in REAUTHENTICATION")
            return False

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def reauthenticate(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. REAUTHENTICATION action just have started!")

        # find and click user-profile-button
        user_profile_button_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//span[@data-testid='user-profile-button']")
        user_profile_button_element.click()

        # find and click Linked Accounts element
        linked_accounts_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//*[contains(text(), 'Linked Accounts')]")
        linked_accounts_element.click()

        # find and click Reauthenticate element
        reauthenticate_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//*[text()='Reauthenticate']")
        reauthenticate_element.click()

        # wait until elements are loaded
        wait_until_element_is_visible(towns_profile, By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # find login_method elements
        login_elements = towns_profile.driver.find_elements(By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
        # get twitter method_element
        twitter_method_element = find_login_method_element(login_elements, "Twitter")
        # click
        twitter_method_element.click()

        # find and click authorize button
        authorize_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//button[@data-testid='OAuth_Consent_Button']")
        authorize_element.click()

        # wait until successful text will appear
        success_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Successfully connected with Twitter')] | //*[contains(text(), 'Authentication failed')]"
        )

        if success_element.text == "Authentication failed":
            error = success_element.find_element(By.XPATH, "..").text
            logger.error(f"Profile_id: {towns_profile.profile_id}. {error}")
            return False
        else:
            towns_profile.linked_accounts.add("TWITTER")
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully LOGINED in TWITTER!")
            return True

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def find_login_method_element(login_elements, method):
    # find twitter_login_method_element
    login_method_element = None
    for element in login_elements:
        if method in element.text:
            login_method_element = element

    return login_method_element
