import time
import random
import threading
import pandas as pd
from numpy import floor, ceil
from typing import List, Dict
from loguru import logger

from src.towns_actions.create_new_town import create_new_town
from src.towns_actions.get_daily_points import get_daily_points
from src.towns_actions.get_info import get_connected_wallet
from src.towns_actions.join_town import join_free_town, join_paid_town
from src.towns_actions.logining import login_twitter, login_google, check_reauthentication, reauthenticate
from src.towns_actions.open_random import open_random_town
from src.towns_actions.open_towns import open_towns
from src.towns_actions.write_message import write_n_messages
from src.towns_profile_manager import TownsProfileManager
from src.okx import okx_withdraw


def run_profile_group(profile_group: List[TownsProfileManager], actions: List[Dict[str, any]]):
    barrier = threading.Barrier(len(profile_group))  # Barrier for write_message synchronization

    # Start threads for each profile
    threads = []
    for profile in profile_group:
        t = threading.Thread(target=run_actions, args=(profile, actions, barrier))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    logger.warning(f"GROUP FINISHED. All profiles completed.")


def run_actions(towns_profile: TownsProfileManager, actions: List[Dict[str, any]]):
    try:
        # Shuffle actions for this profile
        shuffled_actions = arrange_shuffled_actions(actions)

        # 1st action
        towns_profile.open_profile()
        time.sleep(5)

        # 2nd action
        login_need = open_towns(towns_profile)

        # login if needed
        if login_need:
            if towns_profile.login_with == "TWITTER":
                login_twitter(towns_profile)
            elif towns_profile.login_with == "GOOGLE":
                login_google(towns_profile)

        else:
            if check_reauthentication(towns_profile):
                if reauthenticate(towns_profile):
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. Reauthenticate was done successfully.")
                else:
                    raise "Unsuccessful Reauthentication"

        # 3d action
        get_connected_wallet(towns_profile)

        # all other actions
        for action in shuffled_actions:
            if action["action"] == "okx_withdraw":
                withdraw_range = [action["params"]["bottom_limit_range"], action["params"]["top_limit_range"]]
                okx_withdraw(towns_profile.wallet, "ETH", "Base", withdraw_range)

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
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for CREATE DYNAMIC CHANNEL")

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

            # write message action
            if action["action"] == "write_message":
                if random.random() < action["params"]["chance"]:

                    if action["params"]["link"]:
                        town_link = action["params"]["link"]
                    else:
                        town_link = get_random_town_link(towns_profile, action["params"]["town_type"])

                    if not town_link:
                        logger.warning(f"Profile_ID: {towns_profile.profile_id}. NO link with provided parameters. Trying open RANDOM TOWN with membership.")
                    if not town_link:
                        town_link = open_random_town(towns_profile)
                    if town_link:
                        write_n_messages(towns_profile, town_link, action["params"]["number"], action["params"]["cooldown"])
                    else:
                        logger.warning(f"Profile_ID: {towns_profile.profile_id}. WRITE MESSAGE wasn't done due to no link options")
                else:
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for WRITE MESSAGE")

            # get daily points action
            if action["action"] == "get_daily_points":
                if random.random() < action["params"]["chance"]:
                    get_daily_points(towns_profile)
                else:
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for DAILY POINTS")

        towns_profile.close_profile()

    except Exception as e:
        try:
            towns_profile.close_profile()
        except Exception as er:
            logger.error(f"Profile_ID: {towns_profile.profile_id}. {er}")

        logger.error(f"Profile_ID: {towns_profile.profile_id}. {e}")


def run_actions_grouped(towns_profile: TownsProfileManager, actions: List[Dict[str, any]], barrier: threading.Barrier):
    try:
        # Shuffle actions for this profile
        shuffled_actions = arrange_shuffled_actions(actions)

        # 1st action
        towns_profile.open_profile()

        # 2nd action
        login_need = open_towns(towns_profile)

        # login if needed
        if login_need:
            if towns_profile.login_with == "TWITTER":
                login_twitter(towns_profile)
            elif towns_profile.login_with == "GOOGLE":
                login_google(towns_profile)

            get_connected_wallet(towns_profile)
        else:
            if check_reauthentication(towns_profile):
                if reauthenticate(towns_profile):
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. Reauthenticate was done successfully.")
                else:
                    raise "Unsuccessful Reauthentication"

        # all other actions
        for action in shuffled_actions:
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
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for CREATE DYNAMIC CHANNEL")

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

            # write message action
            if action["action"] == "write_message":
                if random.random() < action["params"]["chance"]:
                    # Wait at the barrier until all profiles reach their write_message
                    barrier.wait()

                    if action["params"]["link"]:
                        town_link = action["params"]["link"]
                    else:
                        town_link = get_random_town_link(towns_profile, action["params"]["town_type"])

                    if not town_link:
                        logger.warning(f"Profile_ID: {towns_profile.profile_id}. NO link with provided parameters. Trying open RANDOM TOWN with membership.")
                    if not town_link:
                        town_link = open_random_town(towns_profile)
                    if town_link:
                        write_n_messages(towns_profile, town_link, action["params"]["number"], action["params"]["cooldown"])
                    else:
                        logger.warning(f"Profile_ID: {towns_profile.profile_id}. WRITE MESSAGE wasn't done due to no link options")
                else:
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for WRITE MESSAGE")

            # get daily points action
            if action["action"] == "get_daily_points":
                if random.random() < action["params"]["chance"]:
                    get_daily_points(towns_profile)
                else:
                    logger.info(f"Profile_ID: {towns_profile.profile_id}. BAD LUCK for DAILY POINTS")

        towns_profile.close_profile()

    except Exception as e:
        towns_profile.close_profile()
        logger.error(f"Profile_ID: {towns_profile.profile_id}. {e}")


def arrange_shuffled_actions(actions):
    write_actions = list()
    other_actions = list()
    okx_actions = list()

    for action in actions:
        if action["action"] == "write_message":
            write_actions.append(action)
        elif action["action"] == "okx_withdraw":
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
    if town_type == "STATE":
        priority_lists = [towns_profile.state_towns, towns_profile.dynamic_towns, towns_profile.free_towns]
    elif town_type == "DYNAMIC":
        priority_lists = [towns_profile.dynamic_towns, towns_profile.free_towns]
    elif town_type == "FREE":
        priority_lists = [towns_profile.free_towns]
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
        group_size = random.randint(group_of_n - int(floor(group_of_n * 0.25)), group_of_n + int(ceil(group_of_n * 0.25)))
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


def main_groups(check_csv_file, check_env_file, check_actions_file, load_dotenv, os, logic, parse_actions):
    if check_csv_file() and check_env_file() and check_actions_file():
        logger.info("All files are set correctly")
    else:
        return False

    load_dotenv()
    group_of_n = int(os.getenv('GROUP_OF_N'))

    # create group of profiles to run in concurrent way
    profile_groups = logic.generate_profile_groups(group_of_n)
    # parse actions to perform
    parsed_actions = parse_actions('actions.txt')

    for profile_group in profile_groups:
        logic.run_profile_group(profile_group, parsed_actions)
