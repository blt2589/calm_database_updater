import yaml

from copy_db import run_copy_database
from validate_csv import run_validation
from stage_alt import run_staging
from insert_measurements import run_insert
from helpers.logger import setup_logging

CONFIG_PATH = "/work/scripts/config/update_config.yaml"


def load_config(config_path):
    """
    Load config yaml
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    """
    Run CALM annual update pipeline
    """

    setup_logging()

    print("\nStarting CALM database update pipeline...\n")

    config = load_config(CONFIG_PATH)

    print("01: Copy database")
    run_copy_database(config)

    print("\n02: Validate CSV")
    run_validation(config)

    print("\n03: Stage ALT measurements")
    run_staging(config)

    print("\n04: Insert measurements")
    run_insert(config)

    print("\nCALM database update pipeline completed successfully.")


if __name__ == "__main__":
    main()