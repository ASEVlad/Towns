import os
from loguru import logger
from dotenv import load_dotenv

from src import logic
from src.utils import parse_actions
from src.checks import check_csv_file, check_env_file, check_actions_file


def main():
    logger.add("logfile.log", rotation="10 MB", level="INFO")

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


if __name__ == "__main__":
    main()
