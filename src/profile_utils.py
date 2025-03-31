import os
import requests
from typing import List
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils import get_geckodriver_path


load_dotenv()
ADS_API_URL = os.getenv("ADS_API_URL")


def retrieve_profile_ids() -> List:
    with open("profiles.txt", "r") as file:
        profile_ids = [line.strip() for line in file if line.strip()]

    return profile_ids


def open_profile(anty_type, profile_id):
    if anty_type.upper() == "ADSPOWER":
        return open_ads_power_profile(profile_id)
    elif anty_type.upper() == "DOLPHIN":
        return open_dolphin_profile(profile_id)


def open_ads_power_profile(profile_id):
    # Start the Adspower profile
    start_url = f"{ADS_API_URL}/api/v1/browser/start?user_id={profile_id}"
    response = requests.get(start_url).json()

    ws_url = response["data"]["ws"]["selenium"]

    # Connect Selenium to the running Adspower profile
    options = webdriver.ChromeOptions()
    options.debugger_address = ws_url.replace("ws://", "").replace("/devtools/browser/", "")

    geckodriver_path = get_geckodriver_path()
    print(geckodriver_path)
    service = Service(geckodriver_path)  # Ensure you have the correct path
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def open_dolphin_profile(profile_id):
    start_url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
    response = requests.get(start_url).json()

    port = response["automation"]["port"]

    options = Options()
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')

    geckodriver_path = get_geckodriver_path()
    print(geckodriver_path)
    service = Service(geckodriver_path)  # Ensure you have the correct path
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def close_profile(anty_type, driver, profile_id):
    if anty_type.upper() == "ADSPOWER":
        close_ads_power_profile(driver, profile_id)
    elif anty_type.upper() == "DOLPHIN":
        close_dolphin_profile(driver, profile_id)


def close_ads_power_profile(driver, profile_id):
    driver.quit()

    stop_url = f"{ADS_API_URL}/api/v1/browser/stop?user_id={profile_id}"
    requests.get(stop_url)


def close_dolphin_profile(driver, profile_id):
    driver.quit()

    stop_url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop"
    requests.get(stop_url)
