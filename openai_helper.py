import logging
from openai import OpenAI
from config import OPENAI_API
import random
import numpy as np

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
