import re
import time
import random
from loguru import logger
from selenium.webdriver.common.by import By

from src.gpt_helper.openai_helper import fetch_ai_response
from src.towns_profile_manager import TownsProfileManager
from src.utils import send_keys, trim_stacktrace_error, wait_until_element_is_visible


def write_review(towns_profile: TownsProfileManager, town_link: str):
    try:
        logger.info(f"Profile_id: {towns_profile.profile_id}. WRITE REVIEW action just have started!")

        # open town link
        towns_profile.driver.get(town_link)

        # check if you already a member
        share_link_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Share Town Link')] | //*[contains(text(), 'Share Link')]"
        )
        if share_link_element.text != "Share Town Link":
            logger.info(f"Profile_id: {towns_profile.profile_id}. You are not a member of this town. Can NOT perform WRITE_REVIEW action.")
            return False

        # open review tab
        review_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'Review This Town')]")
        if len(review_elements) == 1:
            review_elements[0].click()
        else:
            logger.info(f"Profile_id: {towns_profile.profile_id}. The review is already written. Can NOT perform WRITE_REVIEW action.")
            return False

        # click write_review button to open box with writing review
        write_review_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//*[contains(text(), 'Write a Review')]")
        write_review_element.click()

        # find an element in the box
        review_element = wait_until_element_is_visible(towns_profile, By.XPATH, ".//textarea[@name='text']")

        # generate and send review
        review_text = generate_review()
        send_keys(review_element, review_text)
        time.sleep(1)

        # find rating element
        num_stars = random.randint(3, 5)
        select_rating_element = towns_profile.driver.find_element("xpath","//*[contains(text(), 'Select your rating')]")
        star_elements = select_rating_element.find_element("xpath", "..").find_elements("xpath", ".//div")
        star_elements[num_stars - 1].click()
        time.sleep(1)

        # click Post_review
        post_review_element = wait_until_element_is_visible(towns_profile, By.XPATH, "//*[contains(text(), 'Post Review')]")
        post_review_element.click()

        # click on Pay_with_ETH
        check_element = wait_until_element_is_visible(
            towns_profile,
            By.XPATH,
            "//*[contains(text(), 'Pay with ETH')] | //*[contains(text(), 'The review does not show engagement')]"
        )
        if "Pay with ETH" in check_element.text:
            check_element.click()
            time.sleep(2)

            # check if you have funds
            not_enough_funds_elements = towns_profile.driver.find_elements(By.XPATH, "//*[contains(text(), 'You need at least')]")
            if len(not_enough_funds_elements) == 1:
                logger.error(f"Profile_id: {towns_profile.profile_id}. Not enough funds")
                return False
        else:
            # find an element in the box
            review_element = wait_until_element_is_visible(towns_profile, By.XPATH, ".//textarea[@name='text']")

            # generate and send additional review
            review_text = generate_review()
            send_keys(review_element, " " + review_text)
            time.sleep(1)

            # Pay with ETH
            pay_with_eth_element = wait_until_element_is_visible(
                towns_profile,
                By.XPATH,
                "//*[contains(text(), 'Pay with ETH')] | //*[contains(text(), 'The review does not show engagement')]"
            )
            pay_with_eth_element.click()

        # Wait till review will be submitted
        wait_until_element_is_visible(towns_profile, By.XPATH, "//*[contains(text(), 'Review posted successfully')]", timeout=60)
        logger.info(f"Profile_id: {towns_profile.profile_id}. Successfully WRITTEN REVIEW!")

    except Exception as e:
        trimmed_error_log = trim_stacktrace_error(str(e))
        logger.error(f"Profile_id: {towns_profile.profile_id}. {trimmed_error_log}")


def generate_review():
    review = fetch_ai_response("generate a review for a discord channel with 10-15 words. Provide only the text of the review.")
    return clean_review(review)


def clean_review(review):
    return re.sub(r'^[^\w]+|[^\w]+$', '', review)
