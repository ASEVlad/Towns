import os
import random
import logging
import requests
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

from data.discord_names import *


load_dotenv()
OPENAI_API = os.getenv("OPENAI_API")
client = OpenAI(api_key=OPENAI_API)


def generate_reply(last_messages):
    """Generates the next message using OpenAI API."""
    if random.random() < 0.05:
        change_topic = "Change topic of the conversation."
    else:
        change_topic = ""

    num_words = max(5, np.floor(random.random() * 100 / 4))

    content_message = f"""
    Your task is to generate next message, please. Make them short and ready to send (I do not want to change anything in them.)
    {change_topic}. Make next message of {num_words} words.
    
    Here is the flow of messages in the chat:
    {last_messages[0]}\n
    {last_messages[1]}\n
    {last_messages[2]}\n
    {last_messages[3]}\n
    {last_messages[4]}\n
    
    Generate next message, please.
    """

    messages = [{"role": "user", "content": content_message}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating response from OpenAI: {e}")
        return None


def generate_username():
    random_unusual_discord_usernames = random.sample(unusual_discord_usernames, 5)
    content_message = f"""
    Generate discord username.
    Provide only the generated name.
    
    Here are the examples:
    Generate discord username. Answer: {random_unusual_discord_usernames[0]}
    Generate discord username. Answer: {random_unusual_discord_usernames[1]}
    Generate discord username. Answer: {random_unusual_discord_usernames[2]}
    Generate discord username. Answer: {random_unusual_discord_usernames[3]}
    Generate discord username. Answer: {random_unusual_discord_usernames[4]}

    Now generate new one similar to the names in the examples.
    Generate discord username. Answer: """

    messages = [{"role": "user", "content": content_message}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        return None


def generate_town_name():
    random_unusual_discord_channels = random.sample(unusual_discord_channels, 5)
    content_message = f"""
    Generate discord channel name.
    Provide only the generated name.
    
    Here are the examples:
    Generate discord channel name. Answer: {random_unusual_discord_channels[0]}
    Generate discord channel name. Answer: {random_unusual_discord_channels[1]}
    Generate discord channel name. Answer: {random_unusual_discord_channels[2]}
    Generate discord channel name. Answer: {random_unusual_discord_channels[3]}
    Generate discord channel name. Answer: {random_unusual_discord_channels[4]}

    Now generate new one similar to the names in the examples.
    Generate discord channel name. Answer: """

    messages = [{"role": "user", "content": content_message}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        return None


def generate_town_logo(town_name):
    basic_colors = ["red", "blue", "green", "yellow", "orange", "purple", "black", "white", "brown", "gray"]
    random_colors = random.sample(basic_colors, 2)

    response = client.images.generate(
        model="dall-e-2",
        prompt=f"A modern discord channel logo with the name {town_name} with minimalist design, {random_colors[0]} and {random_colors[1]} color theme",
        n=1,  # Number of images to generate
        size="256x256"  # Image size
    )

    # Get the generated image URL
    logo_url = response.data[0].url

    # Download and save the image
    path_to_logos = "towns_images"
    num_of_existed_logos = len(os.listdir(path_to_logos))

    logo_path = os.path.join(path_to_logos, f"town_logo_{num_of_existed_logos}.png")
    logo_data = requests.get(logo_url).content
    with open(logo_path, "wb") as file:
        file.write(logo_data)

    abs_logo_path = os.path.join(os.getcwd(), logo_path)

    return abs_logo_path
