import os
import requests
import json
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils import get_geckodriver_path


class TownsProfileManager:
    def __init__(self, profile_id: str, anty_type: str, login_with: str):
        self.profile_id = profile_id
        self.anty_type = anty_type.upper()
        self.login_with = login_with.upper()

        self.wallet : str = ""
        self.free_towns : list = list()
        self.state_towns : list = list()
        self.dynamic_towns : list = list()
        self.driver : webdriver = None
        self.linked_accounts : set = set()

        # Read profile parameters from file
        self.load_profile_data()

        load_dotenv()
        if self.anty_type == "ADSPOWER":
            self.ADS_API_URL = os.getenv("ADS_API_URL")

    def load_profile_data(self):
        try:
            with open(os.path.join("data", "profiles_data.json"), "r") as file:
                profiles = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            profiles = {}

        profile_data = profiles.get(self.profile_id, {})
        self.state_towns = profile_data.get("state_towns", list())
        self.dynamic_towns = profile_data.get("dynamic_towns", list())
        self.free_towns = profile_data.get("free_towns", list())
        self.wallet = profile_data.get("wallet", "")
        self.linked_accounts = set(profile_data.get("linked_accounts", list()))

    def save_profile_data(self):
        try:
            with open(os.path.join("data", "profiles_data.json"), "r") as file:
                profiles = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            profiles = {}

        profiles[self.profile_id] = {
            "state_towns": self.state_towns,
            "dynamic_towns": self.dynamic_towns,
            "free_towns": self.free_towns,
            "wallet": self.wallet,
            "linked_accounts": list(self.linked_accounts)
        }

        with open(os.path.join("data", "profiles_data.json"), "w") as file:
            json.dump(profiles, file, indent=4)

    def open_profile(self):
        if self.anty_type == "ADSPOWER":
            self.driver = self.open_ads_power_profile()
        elif self.anty_type == "DOLPHIN":
            self.driver = self.open_dolphin_profile()
        return self.driver

    def open_ads_power_profile(self):
        start_url = f"{self.ADS_API_URL}/api/v1/browser/start?user_id={self.profile_id}"
        response = requests.get(start_url).json()
        ws_url = response["data"]["ws"]["selenium"]

        options = webdriver.ChromeOptions()
        options.debugger_address = ws_url.replace("ws://", "").replace("/devtools/browser/", "")

        geckodriver_path = get_geckodriver_path()
        service = Service(geckodriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def open_dolphin_profile(self):
        start_url = f"http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1"
        response = requests.get(start_url).json()
        port = response["automation"]["port"]

        options = Options()
        options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')

        geckodriver_path = get_geckodriver_path()
        service = Service(geckodriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def close_profile(self):
        self.save_profile_data()

        if self.driver:
            self.driver.close()
            self.driver.quit()

        if self.anty_type == "ADSPOWER":
            stop_url = f"{self.ADS_API_URL}/api/v1/browser/stop?user_id={self.profile_id}"
        elif self.anty_type == "DOLPHIN":
            stop_url = f"http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop"

        requests.get(stop_url)
        self.driver = None
