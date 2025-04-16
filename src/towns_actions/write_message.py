import os
import time
import json
import random
import threading
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import Dict, List
from numpy import floor, ceil
from selenium.webdriver.common.by import By

from src.towns_actions.new_town import enter_username
from src.towns_actions.update_towns import update_towns
from src.utils import send_keys, trim_stacktrace_error, clean_text, wait_until_element_is_visible
from data.lists import basic_colors, topics
from src.gpt_helper.openai_helper import fetch_ai_response
from src.towns_profile_manager import TownsProfileManager

message_lock = threading.Lock()
MESSAGE_STORE = Path(os.path.join("data", "messages.json"))


def write_n_messages(towns_profile: TownsProfileManager, town_link, n_messages=1, time_delay=15):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. WRITE MESSAGES action just have started!")

        # open town
        towns_profile.driver.get(town_link)

        time.sleep(random.uniform(0, time_delay))

        # check if profile is a member of the town
        check_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]",
            timeout=60
        )

        # check if profile is a member of the town
        if "Share Town Link" not in check_element.text:
            logger.info(f"You are not a member of this town. Link: {town_link}")
            return False

        # Enter username if needed
        enter_username(towns_profile)

        # join general channel if needed
        join_general_channel(towns_profile)

        # wait till Send_message element is loaded
        new_message_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[@data-testid='send-message-text-box']"
        )

        # Enter username if needed
        enter_username(towns_profile)

        for i in range(n_messages):
            # try update towns
            try_update_towns(towns_profile)

            # get last 5 messages
            last_messages = get_last_messages_locally(town_link, n=5)

            # generate next message
            prompt = generate_prompt(last_messages, towns_profile.wallet)
            next_message = fetch_ai_response(prompt)
            next_message_cleaned = clean_text(next_message)

            # find textbox and type next_message
            new_message_element = new_message_element.find_element(By.XPATH, "..").find_element(By.XPATH, "//div[@role='textbox']")
            send_keys(new_message_element, next_message_cleaned)
            time.sleep(1)

            # find and click send button
            send_message_element = towns_profile.driver.find_element(By.XPATH, "//button[@type='button' and @data-testid='submit']")
            send_message_element.click()

            store_message(town_link, towns_profile.wallet, next_message_cleaned)

            # wait some time
            time.sleep(random.randint(int(floor(time_delay - time_delay / 5)), int(ceil(time_delay - time_delay / 5))))
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully WRITTEN MESSAGE!")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def get_last_messages(towns_profile, n_messages=5):
    # find messages
    message_elements = towns_profile.driver.find_elements(By.XPATH, "//div[@data-testid='chat-message-container']")

    messages = list()
    errors = 0
    i = 0

    while len(messages) < n_messages and i < len(message_elements):
        try:
            # find message text
            message_text = message_elements[-i].find_element(By.TAG_NAME, "p").text
            if "Waiting for message to decrypt" not in message_text:
                messages.append(message_text)
        except:
            errors += 1
        i += 1

    if len(messages) == 0:
        logger.info("Decrypting problem!")

    return messages


def generate_prompt(last_messages, current_wallet):
    if len(last_messages) > 0:
        if random.random() < 1/13:
            random_topic = random.sample(basic_colors, 1)[0]
            change_topic = f"Change topic of the conversation on {random_topic}"
        else:
            change_topic = ""

        flow_of_messages = generate_message_flow(last_messages, current_wallet)

        mean_limit_words = random.randint(3, 15)
        low_limit_words = max(2, mean_limit_words - random.randint(1, 3))
        top_limit_words = max(3, mean_limit_words + random.randint(1, 3))

        content_message = f"""
You are a casual Discord chat participant in your teens/early 20s. Your task is to continue the conversation naturally based on the previous messages.
Rules:
- Keep responses between {low_limit_words}-{top_limit_words} words
- Stay in context of the conversation
- Be casual and informal, like a real Discord user
- Use minimal punctuation (occasional commas are ok)
- Do not use any smiles
- Don't overuse exclamation marks
- Never mention that you're an AI
- It's ok to make small typos sometimes
- Mix up your style - don't be repetitive with phrases
- Generate only message without anything else. Just plain text.

{change_topic}.

Here is the flow of messages in the chat.
{flow_of_messages}

Generate next message, please.
You: """
    else:
        random_topic = random.sample(topics, 1)[0]
        content_message = f"""
You are a casual Discord chat participant in your teens/early 20s. Your task is to start the conversation.
Rules:
- Keep responses between 3-15 words
- Stay in context of the conversation
- Be casual and informal, like a real Discord user
- Use minimal punctuation (occasional commas are ok)
- Don't overuse exclamation marks
- Never mention that you're an AI
- It's ok to make small typos sometimes
- Mix up your style - don't be repetitive with phrases
- Generate only message without anything else. Just plain text.
Topic: {random_topic}

Generate first message, please.
        """

    return content_message


def generate_message_flow(last_messages, current_wallet):
    message_flow = ""
    persons = dict()

    for message_info in last_messages:
        if current_wallet == message_info.get("sender", ""):
            message_flow += f"You: {message_info.get('text', '')}\n"
        else:
            if message_info.get("sender", "") not in persons:
                persons[message_info.get("sender", "")] = len(persons) + 1
            message_flow += f"Person_{persons.get(message_info.get("sender", ""), 0)}: {message_info.get("text")}\n"
    return message_flow[:-1]


def store_message(town_link: str, sender_wallet: str, text: str, channel_name: str ="general"):
    try:
        messages = load_messages()

        timestamp = datetime.now().isoformat()
        msg = {"sender": sender_wallet, "text": text, "timestamp": timestamp}

        # Ensure town and channel exist
        if town_link not in messages:
            messages[town_link] = {}
        if channel_name not in messages[town_link]:
            messages[town_link][channel_name] = []

        # Append message
        messages[town_link][channel_name].append(msg)

        # Save back to file
        with message_lock:
            with open(MESSAGE_STORE, "w") as f:
                json.dump(messages, f, indent=2)
    except Exception as e:
        logger.error(f"Error storing message: {e}")


def load_messages():
    with message_lock:
        if MESSAGE_STORE.exists():
            with open(MESSAGE_STORE, "r") as f:
                return json.load(f)
        return {}  # return empty dict if file doesn't exist


def get_last_messages_locally(town_link: str, channel_name: str = "general", n: int = 5) -> List[Dict[str, str]]:
    """Retrieve the last n messages from a given town and channel."""
    try:
        messages = load_messages()
        town = messages.get(town_link, {})
        channel = town.get(channel_name, [])
        return channel[-n:]  # Return last n messages (or fewer if not enough)
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []


def join_general_channel(towns_profile):
    el = towns_profile.driver.find_elements(By.XPATH, "//button[contains(text(), 'Join Channel')]")
    if len(el) > 0:
        el[0].click()
        time.sleep(2)

def try_update_towns(towns_profile: TownsProfileManager, chance: float = 0.2):
    if random.random() < chance:
        update_towns(towns_profile)