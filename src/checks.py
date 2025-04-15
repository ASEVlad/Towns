import os
import pandas as pd
from loguru import logger
from dotenv import load_dotenv

from src.utils import parse_actions


def check_csv_file(file_path: str = "profiles.csv") -> bool:
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check 1: Exactly 3 columns with specific names
        expected_columns = {'profile_id', 'anty_type', 'login_with'}
        actual_columns = set(df.columns)
        if actual_columns != expected_columns:
            logger.error(f"Expected columns {expected_columns}, but found {actual_columns}")
            return False

        # Check 2: Unique values of anty_type in {"DOLPHIN", "ADSPOWER"}
        anty_types = set(df['anty_type'].str.upper().unique())
        allowed_anty_types = {"DOLPHIN", "ADSPOWER"}
        if not anty_types.issubset(allowed_anty_types):
            logger.error(f"anty_type values {anty_types} are not in {allowed_anty_types}")
            return False

        # Check 3: Unique values of login_with in {"TWITTER", "GOOGLE"}
        login_withs = set(df['login_with'].str.upper().unique())
        allowed_login_withs = {"TWITTER", "GOOGLE"}
        if not login_withs.issubset(allowed_login_withs):
            logger.error(f"login_with values {login_withs} are not in {allowed_login_withs}")
            return False

        logger.info("profiles.csv file checks completed successfully.")
        return True

    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
        return False
    except pd.errors.EmptyDataError:
        logger.error(f"File '{file_path}' is empty.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


def check_env_file(env_file_path: str = '.env') -> bool:
    # Load the .env file
    load_dotenv(env_file_path)

    # Check if OPENAI_API is present
    openai_api = os.getenv('OPENAI_API')
    if openai_api is None or openai_api.strip() == '':
        logger.error("OPENAI_API is not set in the .env file or is empty.")
        return False

    # Check and set ADS_API_URL if not provided
    ads_api_url = os.getenv('ADS_API_URL')
    if ads_api_url is None or ads_api_url.strip() == '':
        default_url = 'http://127.0.0.1:50325'
        os.environ['ADS_API_URL'] = default_url
        logger.info(f"ADS_API_URL not provided, set to default: {default_url}")

    # Check and set GROUP_OF_N if not provided
    group_of_n = os.getenv('PARALLEL_ACCOUNTS')
    if group_of_n is None or group_of_n.strip() == '':
        default_n = '1'
        os.environ['PARALLEL_ACCOUNTS'] = default_n
        logger.info(f"PARALLEL_ACCOUNTS not provided, set to default: {default_n}")

    logger.info(".env file checks completed successfully.")
    return True


def check_actions_file(file_path: str = "actions.txt") -> bool:
    """
    Check if the actions file is valid and can be parsed correctly.
    Returns False if there are any errors, True otherwise.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"Actions file not found: {file_path}")
        return False

    # Check if file is readable
    try:
        with open(file_path, 'r') as file:
            file.read()
    except Exception as e:
        logger.error(f"Failed to read actions file {file_path}: {str(e)}")
        return False

    try:
        # Parse the actions
        actions = parse_actions(file_path)

        if not actions:
            logger.warning(f"No valid actions found in {file_path}")
            return True  # Not an error, just empty or all comments

        # Valid action names from the README
        valid_actions = {
            "create_free_channel",
            "create_dynamic_channel",
            "create_state_channel",
            "join_free_channel",
            "join_dynamic_channel",
            "join_state_channel",
            "write_message",
            "get_daily_points",
            "okx_withdraw",
            "binance_withdraw",
            "set_profile_avatar",
            "write_review"
        }

        # Valid parameters for each action (based on README)
        valid_params = {
            "create_free_channel": {"chance"},
            "create_dynamic_channel": {"chance"},
            "create_state_channel": {"chance", "cost"},
            "join_free_channel": {"chance"},
            "join_dynamic_channel": {"chance", "cost_limit"},
            "join_state_channel": {"chance", "cost_limit", "link"},
            "write_message": {"chance", "town_type", "number", "cooldown", "link"},
            "get_daily_points": {"chance"},
            "okx_withdraw": {"bottom_limit_range", "top_limit_range", "network"},
            "binance_withdraw": {"bottom_limit_range", "top_limit_range", "network"},
            "set_profile_avatar": {"chance"},
            "write_review": {"chance", "town_type", "link"}
        }

        # Check each action
        for action_dict in actions:
            action_name = action_dict["action"]
            params = action_dict["params"]

            # Check if action is valid
            if action_name not in valid_actions:
                logger.error(f"Invalid action name: {action_name}")
                return False

            # Check if parameters are valid for this action
            valid_param_set = valid_params[action_name]
            for param in params.keys():
                if param not in valid_param_set:
                    logger.error(f"Invalid parameter '{param}' for action '{action_name}'")
                    return False

            # Validate parameter values
            if "chance" in params:
                chance = params["chance"]
                if not isinstance(chance, (int, float)) or chance < 0 or chance > 1:
                    logger.error(f"Invalid chance value {chance} for action {action_name} - must be between 0 and 1")
                    return False

            if "cost" in params:
                cost = params["cost"]
                if not isinstance(cost, (int, float)) or cost < 0:
                    logger.error(f"Invalid cost value {cost} for action {action_name} - must be non-negative")
                    return False

            if "cost_limit" in params:
                cost_limit = params["cost_limit"]
                if not isinstance(cost_limit, (int, float)) or cost_limit < 0:
                    logger.error(f"Invalid cost_limit value {cost_limit} for action {action_name} - must be non-negative")
                    return False

            if "number" in params:
                number = params["number"]
                if not isinstance(number, int) or number < 0:
                    logger.error(f"Invalid number value {number} for action {action_name} - must be non-negative integer")
                    return False

            if "cooldown" in params:
                cooldown = params["cooldown"]
                if not isinstance(cooldown, (int, float)) or cooldown < 0:
                    logger.error(f"Invalid cooldown value {cooldown} for action {action_name} - must be non-negative")
                    return False

            if "town_type" in params:
                town_type = params["town_type"]
                if town_type not in {"free", "dynamic", "state", "random"}:
                    logger.error(f"Invalid town_type value {town_type} for action {action_name} - must be 'free', 'dynamic', or 'state'")
                    return False

            if "bottom_limit_range" in params:
                bottom_limit_range = params["bottom_limit_range"]
                if not isinstance(bottom_limit_range, (int, float)) or bottom_limit_range < 0:
                    logger.error(f"Invalid bottom_limit_range value {bottom_limit_range} for action {action_name} - must be non-negative")
                    return False

            if "top_limit_range" in params:
                top_limit_range = params["top_limit_range"]
                if not isinstance(top_limit_range, (int, float)) or top_limit_range < 0:
                    logger.error(
                        f"Invalid top_limit_range value {top_limit_range} for action {action_name} - must be non-negative")
                    return False

            if "network" in params:
                network = params["network"]
                if network.lower() not in {"arbitrum", "base"}:
                    logger.error(f"Invalid network value {network} for action {action_name} - must be 'arbitrum" or "base'")
                    return False

        logger.info(f"Actions file {file_path} validated successfully")
        return True

    except Exception as e:
        logger.error(f"Error parsing actions file {file_path}: {str(e)}")
        return False



