import time
import random
from numpy import floor, ceil
from loguru import logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_actions.new_town import enter_username
from src.utils import send_keys, trim_stacktrace_error
from data.lists import basic_colors
from src.gpt_helper.openai_helper import generate_reply
from src.towns_profile_manager import TownsProfileManager


def write_n_messages(towns_profile: TownsProfileManager, town_link, n_messages=1, time_delay=15):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. WRITE MESSAGES action just have started!")

        sent_messages = []

        # open town
        towns_profile.driver.get(town_link)

        # check if profile is a member of the town
        check_element = WebDriverWait(towns_profile.driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]")))

        # check if profile is a member of the town
        if "Share Town Link" not in check_element.text:
            logger.info(f"You are not a member of this town. Link: {town_link}")
            return False

        # Enter username if needed
        enter_username(towns_profile)

        # wait till Send_message element is loaded
        new_message_element = WebDriverWait(towns_profile.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Send a message to ')]")))

        for i in range(n_messages):
            # find messages
            message_elements = towns_profile.driver.find_elements(By.XPATH, "//div[@data-testid='chat-message-container']")

            # get last 5 messages
            last_messages = get_last_n_messages(message_elements, 5)

            # generate next message
            prompt = generate_prompt(last_messages, sent_messages)
            next_message = generate_reply(prompt)

            # find textbox and type next_message
            new_message_element = new_message_element.find_element(By.XPATH, "..").find_element(By.XPATH, "//div[@role='textbox']")
            send_keys(new_message_element, next_message)
            time.sleep(1)

            # find and click send button
            send_message_element = towns_profile.driver.find_element(By.XPATH, "//button[@type='button' and @data-testid='submit']")
            send_message_element.click()

            sent_messages.append(next_message)

            # wait some time
            time.sleep(random.randint(int(floor(time_delay - time_delay / 5)), int(ceil(time_delay - time_delay / 5))))
            logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully WRITTEN MESSAGE!")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def get_last_n_messages(message_elements, n_messages=5):
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


def generate_prompt(last_messages, sent_messages):
    if len(last_messages) >= 0:
        if random.random() < 0.05:
            random_topic = random.sample(basic_colors, 1)[0]
            change_topic = f"Change topic of the conversation on {random_topic}"
        else:
            change_topic = ""

        flow_of_messages = generate_message_flow(last_messages, sent_messages)

        content_message = f"""
You are a casual Discord chat participant in your teens/early 20s. Your task is to continue the conversation naturally based on the previous messages.
Rules:
- Keep responses between 3-15 words
- Stay in context of the conversation
- Be super casual and informal, like a real Discord user
- Use minimal punctuation (occasional commas are ok)
- Use slang sparingly
- Do not use any smiles
- Don't overuse exclamation marks
- Never mention that you're an AI
- It's ok to make small typos sometimes
- Mix up your style - don't be repetitive with phrases

{change_topic}.

Here is the flow of messages in the chat.
{flow_of_messages}

Generate next message, please.
        """
    else:
        content_message = f"""
You are a casual Discord chat participant in your teens/early 20s. Your task is to start the conversation.
Rules:
- Keep responses between 3-15 words
- Stay in context of the conversation
- Be super casual and informal, like a real Discord user
- Use minimal punctuation (occasional commas are ok)
- Use slang sparingly
- Don't overuse exclamation marks
- Never mention that you're an AI
- It's ok to make small typos sometimes
- Mix up your style - don't be repetitive with phrases

Generate first message, please.
        """

    return content_message


def generate_message_flow(last_messages, sent_messages):
    message_flow = ""
    for message in last_messages:
        if message in sent_messages:
            message_flow += f"Your message: {message}\n"
        else:
            message_flow += f"Smbd's message: {message}\n"
    return message_flow[:-1]
