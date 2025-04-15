import time
import random
import threading
import pandas as pd
from numpy import floor
from typing import List, Dict
from loguru import logger

from src.towns_actions.write_review import write_review
from src.withdraw import binance_withdraw, okx_withdraw, wait_for_balance
from src.towns_actions.new_town import create_new_town, join_free_town, join_paid_town
from src.towns_actions.get_daily_points import get_daily_points
from src.towns_actions.profile_info import get_connected_wallet, set_profile_avatar, get_existed_towns
from src.towns_actions.logining import login_twitter, login_google, check_reauthentication, reauthenticate
from src.towns_actions.open_towns import open_towns
from src.towns_actions.write_message import write_n_messages
from src.towns_profile_manager import TownsProfileManager
from src.utils import extract_wallets_to_file, trim_stacktrace_error


def run_profile_group(profile_group: List, actions: List[Dict[str, any]]):
    if len(profile_group) == 1:
        barrier = None
    else:
        barrier = threading.Barrier(len(profile_group))

    threads = []
    for profile in profile_group:
        t = threading.Thread(
            target=run_actions,
            args=(profile, actions, barrier)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info("GROUP FINISHED. All profiles completed.")


def run_actions(towns_profile: TownsProfileManager, actions: List[Dict[str, any]], barrier=None):
    try:
        shuffled_actions = arrange_shuffled_actions(actions)
        execute_initial_actions(towns_profile)

        for action in shuffled_actions:
            handle_action(towns_profile, action, barrier)

        finalize_profile(towns_profile)
    except Exception as e:
        handle_error(towns_profile, e)
        barrier.abort()


def execute_initial_actions(towns_profile):
    towns_profile.open_profile()
    time.sleep(5)

    if open_towns(towns_profile):
        authenticate_user(towns_profile)

    if not towns_profile.wallet:
        get_connected_wallet(towns_profile)

    if not towns_profile.other_towns:
        get_existed_towns(towns_profile)


def authenticate_user(towns_profile):
    # login if needed
    if towns_profile.login_with == "TWITTER":
        login_twitter(towns_profile)
    elif towns_profile.login_with == "GOOGLE":
        login_google(towns_profile)

    if check_reauthentication(towns_profile):
        if reauthenticate(towns_profile):
            logger.info(f"Profile_ID: {towns_profile.profile_id}. Reauthenticate was done successfully.")
        else:
            raise "Unsuccessful Reauthentication"


def handle_action(towns_profile, action, barrier=None):
    if action["action"] in ["okx_withdraw", "binance_withdraw"]:
        process_withdrawal(towns_profile, action)
    elif action["action"].startswith("create_"):
        process_create_channel(towns_profile, action)
    elif action["action"].startswith("join_"):
        process_join_channel(towns_profile, action)
    elif action["action"] == "get_daily_points":
        process_daily_points(towns_profile, action)
    elif action["action"] == "set_profile_avatar":
        process_set_profile_avatar(towns_profile, action)
    elif action["action"] == "write_message":
        process_write_message(towns_profile, action, barrier)
    elif action["action"] == "write_review":
        process_write_review(towns_profile, action)


# Extract repetitive action handling logic
def process_withdrawal(towns_profile, action):
    if action["action"] == "okx_withdraw":
        if towns_profile.wallet:
            withdraw_range = [action["params"]["bottom_limit_range"], action["params"]["top_limit_range"]]
            withdraw_amount = okx_withdraw(towns_profile.wallet, withdraw_range, "ETH", action["params"]["network"])

    if action["action"] == "binance_withdraw":
        if towns_profile.wallet:
            withdraw_range = [action["params"]["bottom_limit_range"], action["params"]["top_limit_range"]]
            withdraw_amount = binance_withdraw(towns_profile.wallet, withdraw_range, "ETH", action["params"]["network"])

    if withdraw_amount:
        wait_for_balance(towns_profile.wallet, withdraw_amount, action["params"]["network"], max_time_to_wait=30)


def process_create_channel(towns_profile, action):
    # create channel actions
    if action["action"] == "create_free_channel":
        if random.random() < action["params"]["chance"]:
            create_new_town(towns_profile, "free")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for CREATE FREE CHANNEL")

    if action["action"] == "create_dynamic_channel":
        if random.random() < action["params"]["chance"]:
            create_new_town(towns_profile, "dynamic")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for CREATE DYNAMIC CHANNEL")

    if action["action"] == "create_state_channel":
        if random.random() < action["params"]["chance"]:
            create_new_town(towns_profile, "state", action["params"]["cost"])
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for CREATE STATE CHANNEL")


def process_join_channel(towns_profile, action):
    # join town actions
    if action["action"] == "join_free_channel":
        if random.random() < action["params"]["chance"]:
            town_link = get_new_random_town_link(towns_profile, "free")
            if town_link:
                join_free_town(towns_profile, town_link)
            else:
                logger.warning(f"Profile_ID: {towns_profile.profile_id}. JOIN FREE CHANNEL wasn't done due to no link options")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for JOIN FREE CHANNEL")

    if action["action"] == "join_dynamic_channel":
        if random.random() < action["params"]["chance"]:
            town_link = get_new_random_town_link(towns_profile, "dynamic")
            if town_link:
                join_paid_town(towns_profile, town_link, "dynamic", upper_limit=action["params"]["cost_limit"])
            else:
                logger.warning(f"Profile_ID: {towns_profile.profile_id}. JOIN DYNAMIC CHANNEL wasn't done due to no link options")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for JOIN DYNAMIC CHANNEL")

    if action["action"] == "join_state_channel":
        if random.random() < action["params"]["chance"]:
            if action["params"]["link"]:
                town_link = action["params"]["link"]
            else:
                town_link = get_new_random_town_link(towns_profile, "state")

            if town_link:
                join_paid_town(towns_profile, town_link, "state", upper_limit=action["params"]["cost_limit"])
            else:
                logger.warning(f"Profile_ID: {towns_profile.profile_id}. JOIN STATE CHANNEL wasn't done due to no link options")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for JOIN STATE CHANNEL")


def process_write_message(towns_profile: TownsProfileManager, action: Dict[str, Dict], barrier: threading.Barrier = None):
    if barrier:
        try:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. Waiting for barrier to WRITE MESSAGE.")
            barrier.wait()  # no timeout
        except threading.BrokenBarrierError:
            pass

    # write message action
    if action["action"] == "write_message":
        if random.random() < action["params"]["chance"]:

            if action["params"]["link"]:
                # check if link is set in parameters
                town_link = action["params"]["link"]
            else:
                # if link is not set in parameters -> try to get some link from the Profile parameters
                town_link = get_random_town_link(towns_profile, action["params"]["town_type"])

            if town_link:
                # if some town was opened -> write message
                write_n_messages(towns_profile, town_link, action["params"]["number"], action["params"]["cooldown"])
            else:
                logger.warning(
                    f"Profile_ID: {towns_profile.profile_id}. WRITE MESSAGE wasn't done due to no link error")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for WRITE MESSAGE")


def process_daily_points(towns_profile, action):
    # get daily points action
    if action["action"] == "get_daily_points":
        if random.random() < action["params"]["chance"]:
            get_daily_points(towns_profile)
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for DAILY POINTS")


def process_set_profile_avatar(towns_profile, action):
    # get daily points action
    if action["action"] == "set_profile_avatar":
        if random.random() < action["params"]["chance"]:
            set_profile_avatar(towns_profile)
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for SET PROFILE AVATAR")


def process_write_review(towns_profile, action):
    if action["action"] == "write_review":
        if random.random() < action["params"]["chance"]:
            if action["params"]["link"]:
                town_link = action["params"]["link"]
            else:
                town_link = get_random_town_link(towns_profile, action["params"]["town_type"])

            if town_link:
                write_review(towns_profile, town_link)
            else:
                logger.warning(f"Profile_ID: {towns_profile.profile_id}. WRITE REVIEW wasn't done due to no link error")
        else:
            logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for JOIN STATE CHANNEL")


# Finalize the profile (extracted logic)
def finalize_profile(towns_profile):
    extract_wallets_to_file()
    towns_profile.close_profile()


# Consolidated error handling
def handle_error(towns_profile, error):
    trimmed_error_log = trim_stacktrace_error(str(error))
    logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")

    try:
        finalize_profile(towns_profile)
    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def arrange_shuffled_actions(actions):
    write_actions = list()
    other_actions = list()
    okx_actions = list()

    for action in actions:
        if action["action"] == "write_message":
            write_actions.append(action)
        elif "withdraw" in action["action"]:
            okx_actions.append(action)
        else:
            other_actions.append(action)

    shuffled_other_actions = other_actions.copy()
    random.shuffle(shuffled_other_actions)

    return okx_actions + shuffled_other_actions + write_actions


def get_random_town_link(towns_profile, town_type):
    """
    Select a random town link based on the specified town_type.
    If no towns are available in the specified type, fallback to levels below:
    STATE -> DYNAMIC -> FREE
    """
    if town_type.upper() == "RANDOM":
        all_towns = towns_profile.state_towns + towns_profile.dynamic_towns + towns_profile.free_towns + towns_profile.other_towns
        return random.choice(all_towns)

    if town_type.upper() == "STATE":
        priority_lists = [towns_profile.state_towns, towns_profile.dynamic_towns, towns_profile.free_towns, towns_profile.other_towns]
    elif town_type.upper() == "DYNAMIC":
        priority_lists = [towns_profile.dynamic_towns, towns_profile.free_towns, towns_profile.other_towns]
    elif town_type.upper() == "FREE":
        priority_lists = [towns_profile.free_towns, towns_profile.other_towns]
    else:
        return None  # Invalid town_type

    for town_list in priority_lists:
        if town_list:  # Check if the list is not empty
            return random.choice(town_list)

    return None  # Return None if all lists are empty


def get_new_random_town_link(towns_profile, town_type):
    # Define file paths based on town_type
    if town_type.upper() == "STATE":
        file_path = "data/towns_links/state_towns.txt"
        existing_towns = set(towns_profile.state_towns)
    elif town_type.upper() == "DYNAMIC":
        file_path = "data/towns_links/dynamic_towns.txt"
        existing_towns = set(towns_profile.dynamic_towns)
    elif town_type.upper() == "FREE":
        file_path = "data/towns_links/free_towns.txt"
        existing_towns = set(towns_profile.free_towns)
    else:
        raise ValueError("Invalid town_type. Must be 'STATE', 'DYNAMIC', or 'FREE'")

    # Read the file and get all links
    try:
        with open(file_path, 'r') as file:
            links = {line.strip() for line in file if line.strip()}  # Remove empty lines and whitespace
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")

    # Exclude links that are already in existing_towns
    available_links = list(links - existing_towns)

    # Check if there are any valid new links
    if not available_links:
        return None

    # Return a random new link
    return random.choice(available_links)


def parse_profiles():
    # Read the CSV file
    df = pd.read_csv("profiles.csv")

    # Shuffle the DataFrame rows
    df = df.sample(frac=1).reset_index(drop=True)

    profiles = list()
    for _, profile_info in df.iterrows():
        profiles.append(TownsProfileManager(
            profile_id=profile_info["profile_id"],
            anty_type=profile_info["anty_type"],
            login_with=profile_info["login_with"]
        ))

    return profiles


def generate_profile_groups(group_of_n=5):
    # Read the CSV file
    df = pd.read_csv("profiles.csv")

    # Shuffle the DataFrame rows
    df = df.sample(frac=1).reset_index(drop=True)

    # Generate random group sizes
    group_sizes = []
    remaining = len(df)

    while remaining > 0:
        group_size = random.randint(group_of_n - int(floor(group_of_n * 0.25)), group_of_n + int(floor(group_of_n * 0.25)))
        group_size = min(group_size, remaining)  # Ensure it doesn't exceed available rows
        group_sizes.append(group_size)
        remaining -= group_size

    # Split into groups
    groups = list()
    start = 0
    for size in group_sizes:
        group = []
        for _, profile_info in df.iloc[start:start + size].iterrows():
            group.append(TownsProfileManager(
                profile_id=profile_info["profile_id"],
                anty_type=profile_info["anty_type"],
                login_with=profile_info["login_with"]
            ))
        groups.append(group)
        start += size

    return groups
