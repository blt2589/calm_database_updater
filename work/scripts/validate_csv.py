"""
docker compose run --rm runner python /work/scripts/csv_validator.py
"""
from validators.validate_grid_nodes import (
    validate_duplicate_grid_nodes,
    validate_grid_nodes_exist,
    validate_grid_node_ids_not_blank
)

from validators.validate_req_columns import validate_req_columns
from validators.validate_alt_values import validate_alt_values
from validators.validate_measurement_dates import validate_measurement_dates


from helpers.load_csv import load_csv
from helpers.load_config import load_config



# TODO: other validation checks? require every measurement column not null?

def run_validation(config):
    """
    Run all CSV validation checks
    """
    csv_path = config["input_csv"]
    db_path = config["output_database"]

    print(f"Validating CSV: {csv_path}")
    print(f"Against database: {db_path}")

    df = load_csv(csv_path)

    validate_req_columns(df)
    validate_grid_node_ids_not_blank(df)
    validate_grid_nodes_exist(df, db_path)
    validate_duplicate_grid_nodes(df)
    validate_alt_values(df)
    validate_measurement_dates(df)

    print("\nCSV validation completed successfully.")
    print(f"Rows validated: {len(df)}")


if __name__ == "__main__":
    config = load_config("/work/scripts/config/update_config.yaml")
    run_validation(config)