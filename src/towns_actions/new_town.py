import re
import time
import random
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import send_keys, save_town_link, trim_stacktrace_error
from src.gpt_helper.openai_helper import generate_town_name, generate_town_logo, generate_username


def create_new_town(towns_profile: TownsProfileManager, town_type, cost=0):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. CREATE {town_type.upper()} TOWN action just have started!")

        towns_profile.driver.get("https://app.towns.com/t/new")

        # generate name and image for town
        town_name = generate_town_name()
        logo_path = generate_town_logo(town_name)

        # provide town_logo
        input_image_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@type="file"]')))
        input_image_element.send_keys(logo_path)
        towns_profile.driver.implicitly_wait(0.5)

        # provide town_name
        input_town_name_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Town Name']")))
        send_keys(input_town_name_element, town_name)
        time.sleep(3)

        # click next_button
        next_button_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='next-button']")))
        next_button_element.click()
        time.sleep(3)

        if town_type == "free":
            # click Free button
            free_town_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Free')]")))
            free_town_element.click()
            time.sleep(1)

        elif town_type == "dynamic":
            # click Paid option
            paid_town_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Paid')]")))
            paid_town_element.click()
            time.sleep(1)

            # click Dynamic option
            dynamic_town_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Dynamic')]")))
            dynamic_town_element.click()
            time.sleep(1)

        elif town_type == "state":
            # click Paid option
            paid_town_element = WebDriverWait(towns_profile.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Paid')]")))
            paid_town_element.click()
            time.sleep(2)

            # click Fixed option
            fixed_town_element = WebDriverWait(towns_profile.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Fixed')]")))
            fixed_town_element.click()
            time.sleep(2)

            # enter cost amount for the town
            cost_town_element = WebDriverWait(towns_profile.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@name='slideMembership.membershipCost']")))
            send_keys(cost_town_element, str(cost))
            time.sleep(1)

        # click Create button
        create_town_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='create-town-button']")))
        create_town_element.click()
        time.sleep(4)

        # wait till creation
        while True:
            # find and click on pay_with_ETH button
            pay_with_ETH_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pay with ETH')]")
            if len(pay_with_ETH_elements) == 1:
                pay_with_ETH_elements[0].click()

            # check status
            element = WebDriverWait(towns_profile.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Give it a moment. Building a town takes a village')] | //*[contains(text(), 'You created')]")))
            if "Give it a moment. Building a town takes a village" in element.text:
                pass
            else:
                break
            time.sleep(2)

        enter_username(towns_profile)

        # save town_link
        town_link = towns_profile.driver.current_url
        town_link = town_link[:town_link.rfind("/channels")]
        save_town_link(town_link, town_type)

        if town_type.upper() == "STATE":
            towns_profile.state_towns.append(town_link)
        elif town_type.upper() == "DYNAMIC":
            towns_profile.dynamic_towns.append(town_link)
        elif town_type.upper() == "FREE":
            towns_profile.free_towns.append(town_link)


        logger.info(f"Profile_id: {towns_profile.profile_id}. Town of type {town_type} successfully created")
        return town_link

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def join_free_town(towns_profile: TownsProfileManager, town_link):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. JOIN FREE TOWN action just have started!")
        # open town link
        towns_profile.driver.get(town_link)

        # check if you already a member
        share_link_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]")))
        if share_link_element.text == "Share Town Link":
            logger.info("You are already a member of this town")
            return False

        # wait till the page is loaded
        WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Join for Free')]")))

        # find and click Join button
        button_elements = towns_profile.driver.find_elements(By.XPATH, "//button[@type='button']")
        for button_element in button_elements:
            if "Join for Free" in button_element.text:
                button_element.click()

        WebDriverWait(towns_profile.driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))
        time.sleep(2)

        enter_username(towns_profile)

        towns_profile.free_towns.append(town_link)
        logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully JOINED into free town!")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def join_paid_town(towns_profile: TownsProfileManager, town_link, town_type, upper_limit=0.99):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. JOIN {town_type.upper()} TOWN action just have started!")

        # open town link
        towns_profile.driver.get(town_link)

        # check if you already a member
        share_link_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]")))
        if share_link_element.text == "Share Town Link":
            logger.warning(f"Profile_id: {towns_profile.profile_id}. You are already a member of this town")
            return False

        # find price element
        element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[text()='ETH']")))
        box_price_element = element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(By.XPATH, "..")

        # retrieve the price from element
        pattern = r"ENTRY\n(\d+\.\d+)\nETH"
        match = re.search(pattern, box_price_element.text)
        price = float(match.group(1))
        if upper_limit < price:
            logger.warning(f"Profile_id: {towns_profile.profile_id}. Upper_limit for dynamic towns is not satisfied")
            return False

        # wait till the page is loaded
        WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Join for')]")))

        # find and click Join button
        button_elements = towns_profile.driver.find_elements(By.XPATH, "//button[@type='button']")
        for button_element in button_elements:
            if "Join for" in button_element.text:
                button_element.click()

        while True:
            time.sleep(1)
            # find and click on pay_with_ETH button
            pay_with_ETH_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pay with ETH')]")
            if len(pay_with_ETH_elements) == 1:
                pay_with_ETH_elements[0].click()
                break

        time.sleep(2)
        not_enough_funds_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'You need at least')]")
        if len(not_enough_funds_elements) == 1:
            logger.error(f"Profile_id: {towns_profile.profile_id}. Not enough funds to JOIN the town.")
            raise f"Profile_id: {towns_profile.profile_id}. Not enough funds to JOIN the town."
        else:
            WebDriverWait(towns_profile.driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))
        time.sleep(2)

        # enter username if needed
        enter_username(towns_profile)

        if town_type.upper() == "STATE":
            towns_profile.state_towns.append(town_link)
        elif town_type.upper() == "DYNAMIC":
            towns_profile.dynamic_towns.append(town_link)

        logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully JOINED into {town_type} town!")
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def enter_username(towns_profile):
    # enter username if needed
    username_elements = towns_profile.driver.find_elements(By.XPATH, "//input[@data-testid='town-username-input']")
    if len(username_elements) != 0:
        username_element = username_elements[0]
        if username_element.get_attribute("value") == "":
            username = generate_username()
            send_keys(username_element, username)
        else:
            all_chars = "qwertyuiopasdfghjklzxcvbnm1234567890"
            random_num = random.randint(0, len(all_chars) - 1)
            send_keys(username_element, all_chars[random_num])

        submit_username_element = towns_profile.driver.find_element(By.XPATH,
                                                                    "//button[@data-testid='submit-username-button']")
        submit_username_element.click()
        time.sleep(1)