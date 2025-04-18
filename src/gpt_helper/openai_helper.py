import os
import random
from loguru import logger
import requests
from openai import OpenAI
from dotenv import load_dotenv

from data.lists import *


load_dotenv()
OPENAI_API = os.getenv("OPENAI_API")
client = OpenAI(api_key=OPENAI_API)


def fetch_ai_response(content_message):
    messages = [{"role": "user", "content": content_message}]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating response from OpenAI: {e}")
        raise


def generate_town_logo(town_name) -> str:
    try:
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
        path_to_logos = os.path.join("data", "towns_images")
        num_of_existed_logos = len(os.listdir(path_to_logos))

        logo_path = os.path.join(path_to_logos, f"town_logo_{num_of_existed_logos}.png")
        logo_data = requests.get(logo_url).content
        with open(logo_path, "wb") as file:
            file.write(logo_data)

        abs_logo_path = os.path.join(os.getcwd(), logo_path)

        return abs_logo_path

    except Exception as e:
        logger.error(f"{e}")
        raise


def generate_username_avatar(username) -> str:
    try:
        random_colors = random.sample(basic_colors, 2)

        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Generate modern discord username avatar for username - {username} with minimalist design, no words or letters, {random_colors[0]} and {random_colors[1]} color theme",
            n=1,  # Number of images to generate
            size="1024x1024"  # Image size
        )

        # Get the generated image URL
        logo_url = response.data[0].url

        # Download and save the image
        path_to_logos = os.path.join("data", "avatars_images")
        num_of_existed_logos = len(os.listdir(path_to_logos))

        logo_path = os.path.join(path_to_logos, f"username_avatar_{num_of_existed_logos}.png")
        logo_data = requests.get(logo_url).content
        with open(logo_path, "wb") as file:
            file.write(logo_data)

        abs_logo_path = os.path.join(os.getcwd(), logo_path)

        return abs_logo_path

    except Exception as e:
        logger.error(f"{e}")
        raise
