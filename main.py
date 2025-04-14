from loguru import logger

from src import logic
from src.logic import run_actions
from src.utils import parse_actions
from src.checks import check_csv_file, check_env_file, check_actions_file


def main():
    logger.add("logfile.log", rotation="10 MB", level="INFO")

    if check_csv_file() and check_env_file() and check_actions_file():
        logger.info("All files are set correctly")
    else:
        return False

    # parse profiles
    profile_groups = logic.parse_profiles()

    # parse actions to perform
    parsed_actions = parse_actions('actions.txt')

    for towns_profile in profile_groups:
        run_actions(towns_profile, parsed_actions)


if __name__ == "__main__":
    main()
