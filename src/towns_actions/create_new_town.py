import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import send_keys, save_town_link
from src.gpt_helper.openai_helper import generate_town_name, generate_town_logo, generate_username

def create_new_town(towns_profile: TownsProfileManager, town_type, cost=0):
    towns_profile.driver.get("https://app.towns.com/t/new")

    # generate name and imamge for town
    town_name = generate_town_name()
    logo_path = generate_town_logo(town_name)

    # provide town_logo
    input_image_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, '//input[@type="file"]')))
    input_image_element.send_keys(logo_path)
    towns_profile.driver.implicitly_wait(0.5)

    # provide town_name
    imput_town_name_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Town Name']")))
    send_keys(imput_town_name_element, town_name)
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
    time.sleep(2)

    # wait till creation
    while True:
        # find and click on pay_with_ETH button
        pay_with_ETH_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pay with ETH')]")
        if len(pay_with_ETH_elements) == 1:
            pay_with_ETH_elements[0].click()

        # check status
        element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Give it a moment. Building a town takes a village')] | //*[contains(text(), 'You created')]")))
        if "Give it a moment. Building a town takes a village" in element.text:
            pass
        else:
            break
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

    # save town_link
    town_link = towns_profile.driver.current_url
    town_link = town_link[:town_link.rfind("/channels")]

    save_town_link(town_link, town_type)

    return town_link
