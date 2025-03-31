import os
import time
import requests
import src.pyanty as pyanty
from typing import List
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

load_dotenv()
ADS_API_URL = os.getenv("ADS_API_URL")


def retrieve_profile_ids() -> List:
    with open("profiles.txt", "r") as file:
        profile_ids = [line.strip() for line in file if line.strip()]

    return profile_ids


def open_dolphin_profile(profile_id):
    response = pyanty.run_profile(profile_id)
    port = response['automation']['port']
    driver = pyanty.get_driver(port=port)
    time.sleep(2)

    return driver


def close_dolphin_profile(driver, profile_id):
    driver.quit()
    time.sleep(1)
    pyanty.close_profile(profile_id)


def open_ads_power_profile(profile_id):
    # Start the Adspower profile
    start_url = f"{ADS_API_URL}/api/v1/browser/start?user_id={profile_id}"
    response = requests.get(start_url).json()

    ws_url = response["data"]["ws"]["selenium"]
    print(f"WebSocket Debugging URL: {ws_url}")

    # Connect Selenium to the running Adspower profile
    options = webdriver.ChromeOptions()
    options.debugger_address = ws_url.replace("ws://", "").replace("/devtools/browser/", "")

    service = Service("src/pyanty/chromedriver")  # Ensure you have the correct path
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def close_ads_power_profile(driver, profile_id):
    driver.quit()
    requests.get(f"{ADS_API_URL}/api/v1/browser/stop?user_id={profile_id}")
