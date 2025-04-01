import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.towns_profile_manager import TownsProfileManager
from src.utils import send_keys
from src.gpt_helper.openai_helper import generate_reply
from data.lists import basic_colors


def write_message(towns_profile: TownsProfileManager, town_link):
    # open town
    if town_link not in towns_profile.driver.current_url:
        towns_profile.driver.get(town_link)

    # wait till page is loaded
    new_message_element = WebDriverWait(towns_profile.driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Send a message to ')]")))

    # find messages
    message_elements = towns_profile.driver.find_elements(By.XPATH, "//div[@data-testid='chat-message-container']")

    # get last 5 messages
    last_messages = get_last_n_messages(message_elements, 5)

    # generate next message
    prompt = generate_prompt(last_messages)
    next_message = generate_reply(prompt)

    # find textbox and type next_message
    new_message_element = new_message_element.find_element(By.XPATH, "..").find_element(By.XPATH,
                                                                                        "//div[@role='textbox']")
    send_keys(new_message_element, next_message)
    time.sleep(1)

    # find and click send button
    send_message_element = towns_profile.driver.find_element(By.XPATH, "//button[@type='button' and @data-testid='submit']")
    send_message_element.click()


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
        print("Decrypting problem!")

    return messages


def generate_prompt(last_messages):
    if len(last_messages) >= 0:
        if random.random() < 0.05:
            random_topic = random.sample(basic_colors, 1)[0]
            change_topic = f"Change topic of the conversation on {random_topic}"
        else:
            change_topic = ""

        flow_of_messages = "\n".join(last_messages)

        content_message = f"""
You are a casual Discord chat participant in your teens/early 20s. Your task is to continue the conversation naturally based on the previous messages.
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
