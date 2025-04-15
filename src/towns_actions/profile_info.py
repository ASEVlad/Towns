import time

import pyperclip
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.gpt_helper.openai_helper import generate_username_avatar
from src.towns_actions.new_town import generate_username, enter_username
from src.towns_profile_manager import TownsProfileManager
from src.utils import trim_stacktrace_error, get_full_xpath_element


def get_connected_wallet(towns_profile: TownsProfileManager):
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
        profile_box_element = image_profile_element.find_element(By.XPATH, "..").find_element(By.XPATH,
                                                                                              "..").find_element(
            By.XPATH, "..")

        # find and click on button that copy text
        copy_wallet_element = profile_box_element.find_element(By.XPATH, "//span[contains(text(), '0x')]")
        copy_wallet_element.click()

        return pyperclip.paste()

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
            towns_profile.wallet = retrieve_wallet_with_validation(towns_profile, copy_connected_wallet_in_profile_box)
        else:
            # find and click Linked Wallets button
            linked_wallets_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Linked Wallets')]")))
            linked_wallets_element.click()

            towns_profile.wallet = retrieve_wallet_with_validation(towns_profile, copy_connected_wallet_in_wallets)

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def set_profile_avatar(towns_profile: TownsProfileManager):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. SET PROFILE AVATAR action just have started!")

        # wait till open the page. find user-profile-button
        user_profile_button_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='user-profile-button']")))

        # check if profile_box is already opened
        check_elements = towns_profile.driver.find_elements(By.XPATH, "//span[@data-testid='upload-image-container']")
        if not check_elements:
            # click user-profile-button if Profile box is not opened
            user_profile_button_element.click()

        # find image_profile_element
        new_image_profile_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@data-testid='user-avatar-upload']")))

        username = generate_username()
        avatar_path = generate_username_avatar(username)

        new_image_profile_element.send_keys(avatar_path)
        towns_profile.driver.implicitly_wait(0.5)

        while True:
            try:
                WebDriverWait(towns_profile.driver, 2).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Uploading Image')]")))
            except:
                break

        logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully SET PROFILE AVATAR!")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
        raise


def get_existed_towns(towns_profile):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. RETRIEVING EXISTED TOWNs just have started!")

        # open main page
        towns_profile.driver.get("https://app.towns.com/explore")

        # wait till open the page.
        user_profile_button_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='user-profile-button']")))
        check_elements = towns_profile.driver.find_elements(By.XPATH, "//span[@data-testid='upload-image-container']")
        if not check_elements:
            # click user-profile-button if Profile box is not opened
            user_profile_button_element.click()
        WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='upload-image-container']")))

        # find create_new_town element
        new_town_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//a[@href="/t/new"]')))
        new_town_xpath = get_full_xpath_element(towns_profile.driver, new_town_element)
        time.sleep(2)

        # find left_box element
        left_box_xpath = new_town_xpath[:new_town_xpath.rfind("div[") - 1]
        left_box_element = towns_profile.driver.find_element("xpath", left_box_xpath)

        # find all left_box elements
        left_box_elements = left_box_element.find_elements("xpath", "./div")
        towns_num = len(left_box_elements) - 2

        if towns_num != len(towns_profile.state_towns) + len(towns_profile.dynamic_towns) + len(towns_profile.free_towns):
            for town_element in left_box_elements[2:]:
                # wait till load the page
                WebDriverWait(towns_profile.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, '//a[@href="/t/new"]')))

                # enter username if needed
                enter_username(towns_profile)

                # enter the town
                town_element.click()

                # wait till load the town
                WebDriverWait(towns_profile.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))

                # retrieve town link
                town_link = towns_profile.driver.current_url
                town_link = town_link[:town_link.rfind("/channels")]
                towns_profile.other_towns.append(town_link)
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully RETRIEVED towns link.")
        else:
            logger.info(f"Profile_id: {towns_profile.profile_id}. Nothing to RETRIEVE.")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")
