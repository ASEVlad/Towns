from selenium.webdriver.common.by import By

from src.towns_profile_manager import TownsProfileManager


def update_towns(towns_profile: TownsProfileManager):
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
            except:
                pass
    else:
        print("No element 'Update Towns'")
