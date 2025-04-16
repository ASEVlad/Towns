import os
import re
import time
import json
import random
import platform
import threading
from typing import List, Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

message_lock = threading.Lock()

# Define the allowed actions and their possible arguments with default values
DEFAULT_PARAMS = {
    'create_free_channel': {'chance': 1.0},
    'create_dynamic_channel': {'chance': 1.0},
    'create_state_channel': {'chance': 1.0, 'cost': 0.1},
    'join_free_channel': {'chance': 1.0},
    'join_dynamic_channel': {'chance': 1.0, "cost_limit": 0.001},
    'join_state_channel': {'chance': 1.0, "cost_limit": 0.1, "link": None},
    'write_message': {'chance': 1.0, 'town_type': 'state', 'number': 3, 'cooldown': 20, "link": None},
    'get_daily_points': {'chance': 1.0},
    'okx_withdraw': {'network': "base"},
    'binance_withdraw': {'network': "base"},
    'set_profile_avatar': {'chance': 1.0},
    'write_review': {'chance': 1.0, 'town_type': 'random', "link": None},
}


def get_geckodriver_path():
    system = platform.system()
    architecture = platform.machine()
    driver_path = select_driver_executable(system, architecture)

    return driver_path


def select_driver_executable(system, architecture):
    if system == 'Windows':
        executable_name = 'chromedriver.exe' if '64' in architecture else 'chromedriver_x86.exe'
    elif system == 'Darwin' or (system == 'Linux' and '64' in architecture):
        executable_name = 'chromedriver'
    else:
        raise ValueError("Unsupported operating system or architecture")

    executable_path = os.path.join("data", executable_name)

    if system != 'Windows':
        os.chmod(executable_path, 0o755)

    return executable_path


def get_full_xpath_element(driver, element):
    full_xpath_element = driver.execute_script(
        """function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            };
            if (element instanceof Document) {
                return '/';
            }
            for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                comp.name = element.nodeName;
                comp.position = getPos(element);
            }
            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase() + (comp.position > 1 ? '[' + comp.position + ']' : '');
            }
            return xpath;
        }
        return absoluteXPath(arguments[0]);""",
        element
    )
    return full_xpath_element


def save_town_link(town_link, town_type):
    towns_folder = os.path.join("data", "towns_links")
    towns_links_path = None

    if town_type.upper() == "FREE":
        towns_links_path = os.path.join(towns_folder, "free_towns.txt")
    elif town_type.upper() == "DYNAMIC":
        towns_links_path = os.path.join(towns_folder, "dynamic_towns.txt")
    elif town_type.upper() == "STATE":
        pass

    if not towns_links_path:
        return
    with message_lock:
        with open(towns_links_path, 'a') as file:
            file.write("\n" + town_link)


def send_keys(element, text):
    safe_text = clean_text(text)

    for letter in safe_text:
        element.send_keys(letter)
        time.sleep(random.randint(1, 20)/1000)

def clean_text(text):
    return re.sub(r'[^\x20-\x7E\u0000-\uFFFF]', '', text)


def parse_actions(file_path: str = 'actions.txt') -> List[Dict[str, any]]:
    actions = []

    # Regular expression to match action and optional key=value parameters
    pattern = r'(\w+(?:_\w+)*)(?:\s+-\w+=[\w%]+)*'
    param_pattern = r'-(\w+)=([\S]+)'  # Matches -key=value pairs

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line or line.startswith('#'):  # Skip empty lines or comments
                continue

            # Match the action and its parameters
            match = re.match(pattern, line)
            if match:
                action_name = match.group(1)  # The action (e.g., "write_message")
                params_str = line[len(action_name):].strip()  # The rest of the line with parameters

                # Parse parameters into a dictionary
                params = {}
                for param_match in re.finditer(param_pattern, params_str):
                    key, value = param_match.groups()
                    # Convert value to int or float if applicable, otherwise keep as string
                    if value.endswith('%'):
                        params[key] = float(value.rstrip('%')) / 100  # Convert percentage to decimal
                    elif key in ["number"]:
                        params[key] = int(value)
                    elif key in ["town_type", "link", "network"]:
                        params[key] = value
                    else:
                        params[key] = float(value)

                # Merge default parameters with parsed parameters (parsed params override defaults)
                action_defaults = DEFAULT_PARAMS.get(action_name, {})  # Get defaults or empty dict
                merged_params = {**action_defaults, **params}  # Merge, with parsed params taking precedence

                # Add the action and its parameters to the list
                actions.append({
                    'action': action_name,
                    'params': merged_params
                })

    return actions


def extract_wallets_to_file():
    json_file_path = os.path.join("data", "profiles_data.json")
    output_file_path = os.path.join("data", "towns_wallets.txt")

    # Read the JSON file
    with message_lock:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

    # Extract wallets, filtering out empty strings
    wallets = [profile["wallet"] for profile in data.values() if profile["wallet"]]

    # Write wallets to text file
    with message_lock:
        with open(output_file_path, 'w') as file:
            for wallet in wallets:
                file.write(f"{wallet}\n")


def trim_stacktrace_error(log: str) -> str:
    """
    Keeps only the first two stacktrace lines that start with '#'.
    """
    lines = log.strip().splitlines()
    trimmed_lines = []
    count = 0

    for line in lines:
        if line.strip().startswith("#"):
            if count < 2:
                trimmed_lines.append(line)
                count += 1
            else:
                break
        else:
            trimmed_lines.append(line)

    return "\n".join(trimmed_lines)


# noinspection PyTypeChecker
def wait_until_element_is_visible(towns_profile, by: By, selector: str, timeout: int = 30):
    try:
        return WebDriverWait(towns_profile.driver, timeout).until(EC.visibility_of_element_located((by, selector)))
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        towns_profile.logger.error(f"Profile_id: {towns_profile.profile_id}. {selector} got error.\n{trimmed_error_log}")
        raise