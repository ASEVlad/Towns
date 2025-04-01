import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.gpt_helper.openai_helper import generate_username
from src.towns_profile_manager import TownsProfileManager
from src.utils import *


def join_free_town(towns_profile: TownsProfileManager, town_link):
    # open town link
    towns_profile.driver.get(town_link)

    # check if you already a member
    share_link_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]")))
    if share_link_element.text == "Share Town Link":
        print("You are already a member of this town")
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

    # enter username if needed
    username_elements = towns_profile.driver.find_elements(By.XPATH, "//input[@data-testid='town-username-input']")
    if len(username_elements) != 0:
        username_element = username_elements[0]
        if username_element.get_attribute("value") == "":
            username = generate_username()
            send_keys(username_element, username)

        submit_username_element = towns_profile.driver.find_element(By.XPATH, "//button[@data-testid='submit-username-button']")
        submit_username_element.click()
        time.sleep(1)



def join_paid_town(towns_profile: TownsProfileManager, town_link, upper_limit=0.99):
    # open town link
    towns_profile.driver.get(town_link)

    # check if you already a member
    share_link_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]")))
    if share_link_element.text == "Share Town Link":
        print("You are already a member of this town")
        return False

    # find price element
    element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[text()='ETH']")))
    box_price_element = element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(By.XPATH, "..")

    # retrieve the price from element
    pattern = r"ENTRY\n(\d+\.\d+)\nETH"
    match = re.search(pattern, box_price_element.text)
    price = float(match.group(1))
    if upper_limit < price:
        print("upper_limit for dynamic towns is not satisfied")
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
        print("Not enough funds")
    else:
        WebDriverWait(towns_profile.driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Share Town Link')]")))
    time.sleep(2)

    # enter username if needed
    username_elements = towns_profile.driver.find_elements(By.XPATH, "//input[@data-testid='town-username-input']")
    if len(username_elements) != 0:
        username_element = username_elements[0]
        if username_element.get_attribute("value") == "":
            username = generate_username()
            send_keys(username_element, username)

        submit_username_element = towns_profile.driver.find_element(By.XPATH, "//button[@data-testid='submit-username-button']")
        submit_username_element.click()
        time.sleep(1)
