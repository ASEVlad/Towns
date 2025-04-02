import pyperclip
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager


def get_connected_wallet(towns_profile: TownsProfileManager):
    try:
        # find and click user-profile-button
        user_profile_button_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='user-profile-button']")))
        user_profile_button_element.click()

        # find and click Linked Wallets button
        linked_wallets_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Linked Wallets')]")))
        linked_wallets_element.click()

        # retrieve connected wallet until 2 consecutive wallets are identical
        prev_copied_wallet = None
        while True:
            copied_wallet = copy_connected_wallet(towns_profile)
            if copied_wallet == prev_copied_wallet:
                towns_profile.wallet = copied_wallet

                logger.info(f"Profile_id: {towns_profile.profile_id}. Wallet successfully retrieved!")
                return copied_wallet
            else:
                prev_copied_wallet = copied_wallet
    except Exception as e:
        logger.error(f"Profile_id: {towns_profile.profile_id}. {e}")


def copy_connected_wallet(towns_profile: TownsProfileManager):
    # find element with Town Wallet <p>
    towns_wallet_text_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//p[contains(text(), 'Towns Wallet')]")))
    # find and click on button that copy text
    copy_wallet_element = towns_wallet_text_element.find_element(By.XPATH, "..").find_element(By.XPATH, "span")
    copy_wallet_element.click()

    return pyperclip.paste()
