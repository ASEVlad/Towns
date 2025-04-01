from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager


def login_twitter(towns_profile: TownsProfileManager):
    # find element with Login text
    login_button_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Log In')]")))
    # click Login button
    login_button_element.click()

    # wait untill elements are loaded
    WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")))
    # find login_method elements
    login_elements = towns_profile.driver.find_elements(By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
    # get twitter method_element
    twitter_method_element = find_login_method_element(login_elements, "Twitter")
    # click
    twitter_method_element.click()

    # find authorize button
    autorize_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='OAuth_Consent_Button']")))
    # click
    autorize_element.click()

    # wait until successfull text will appear
    success_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Successfully connected with Twitter')] | //*[contains(text(), 'Authentication failed')]")))

    if success_element.text == "Authentication failed":
        print(success_element.find_element(By.XPATH, "..").text)
        return False
    else:
        return True


def login_google(towns_profile: TownsProfileManager):
    # find element with Login text
    login_button_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Log In')]")))
    # click Login button
    login_button_element.click()

    # wait till elements are visible
    WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")))
    # find login_method elements
    login_elements = towns_profile.driver.find_elements(By.XPATH, "//button[contains(@class, 'LoginMethodButton')]")
    # get and click twitter method_element
    google_method_element = find_login_method_element(login_elements, "Google")
    google_method_element.click()

    # find and click first google account
    login_elements = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@role='link' and @data-item-index='0']")))
    login_elements.click()

    # wait until successfull text will appear
    success_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Successfully connected with Google')] | //*[contains(text(), 'Authentication failed')]")))

    if success_element.text == "Authentication failed":
        print(success_element.find_element(By.XPATH, "..").text)
        return False
    else:
        return True


def find_login_method_element(login_elements, method):
    # find twitter_login_method_element
    login_method_element = None
    for element in login_elements:
        if element.text == method:
            login_method_element = element

    return login_method_element
