import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager


def open_towns(towns_profile: TownsProfileManager):
    # open link
    towns_profile.driver.execute_script(f"window.open('https://app.towns.com/explore', '_blank');")
    towns_profile.driver.implicitly_wait(5)

    # make tab with Towns active
    for handle in reversed(towns_profile.driver.window_handles):  # Iterate in reverse order
        towns_profile.driver.switch_to.window(handle)
        if "Towns" in towns_profile.driver.title:  # Adjust the title check if needed
            break  # Found the correct tab

    # wait till open
    element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='/t/new'] | //*[contains(text(), 'Log In')]")))

    time.sleep(2)

    # return True if Login is needed
    return element.text == "Login"
