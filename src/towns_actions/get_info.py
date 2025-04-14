import pyperclip
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error


def get_connected_wallet(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. GET WALLET action just have started!")

        # wait till open the page. find user-profile-button
        user_profile_button_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='user-profile-button']")))

        # check if profile_box is already opened
        check_elements = towns_profile.driver.find_elements(By.XPATH, "//span[@data-testid='upload-image-container']")
        if not check_elements:
            # click user-profile-button if Profile box is not opened
            user_profile_button_element.click()

        # find image_profile_element
        image_profile_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='upload-image-container']")))

        # find profile_box_element
        profile_box_element = image_profile_element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
            By.XPATH, "..")

        # check if there is already wallet available
        wallet_elements = profile_box_element.find_elements(By.XPATH, "//span[contains(text(), '0x')]")
        if len(wallet_elements) == 1:
            return retrieve_wallet_with_validation(towns_profile, copy_connected_wallet_in_profile_box)
        else:
            # find and click Linked Wallets button
            linked_wallets_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Linked Wallets')]")))
            linked_wallets_element.click()

            return retrieve_wallet_with_validation(towns_profile, copy_connected_wallet_in_wallets)
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def retrieve_wallet_with_validation(towns_profile, copy_wallet_function):
    # retrieve connected wallet until 2 consecutive wallets are identical
    prev_copied_wallet = None
    while True:
        copied_wallet = copy_wallet_function(towns_profile)
        if copied_wallet == prev_copied_wallet:
            towns_profile.wallet = copied_wallet

            logger.info(f"Profile_id: {towns_profile.profile_id}. Wallet successfully retrieved!")
            return copied_wallet
        else:
            prev_copied_wallet = copied_wallet



def copy_connected_wallet_in_wallets(towns_profile: TownsProfileManager):
    # find element with Town Wallet <p>
    towns_wallet_text_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(text(), 'Towns Wallet')]")))
    # find and click on button that copy text
    copy_wallet_element = towns_wallet_text_element.find_element(By.XPATH, "..").find_element(By.XPATH, "span")
    copy_wallet_element.click()

    return pyperclip.paste()


def copy_connected_wallet_in_profile_box(towns_profile: TownsProfileManager):
    # find image_profile_element
    image_profile_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='upload-image-container']")))

    # find profile_box_element
    profile_box_element = image_profile_element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(
        By.XPATH, "..")

    # find and click on button that copy text
    copy_wallet_element = profile_box_element.find_element(By.XPATH, "//span[contains(text(), '0x')]")
    copy_wallet_element.click()

    return pyperclip.paste()
