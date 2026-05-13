"""
docker compose run --rm runner python /work/scripts/csv_validator.py
"""


from pathlib import Path
import sqlite3
import pandas as pd
import yaml
from datetime import datetime

# TODO: other validation checks? require every measurement column not null?


REQUIRED_COLUMNS = [
    "grid_node_id",
    "grid_node_code",
    "latitude",
    "longitude",
    "northing",
    "easting",
    "active_layer_depth_cm_a_raw",
    "active_layer_depth_cm_b_raw",
    "measurement_date",
    "metadata",
]

VALID_ALT_CODES = {"W", "G", "ND", ""}


def load_config(config_path):
    """
    Load config YAML
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_csv(csv_path):
    """
    Load field CSV as text
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    return pd.read_csv(path, dtype=str).fillna("")


def validate_required_columns(df):
    """
    Check all required columns are present
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print("All required columns are present.")


def validate_grid_node_ids_not_blank(df):
    """
    Check every row has grid_node_id
    """
    blank_rows = df[df["grid_node_id"].str.strip() == ""]

    if not blank_rows.empty:
        raise ValueError(
            f"{len(blank_rows)} row(s) have blank grid_node_id values."
        )

    print("No blank grid_node_id values found.")


def get_database_grid_node_ids(db_path):
    """
    Return all grid_node_id values currently in db
    """
    conn = sqlite3.connect(db_path)

    query = "SELECT grid_node_id FROM grid_node;"
    db_ids = pd.read_sql_query(query, conn)["grid_node_id"].astype(str).tolist()

    conn.close()
    return set(db_ids)


def validate_grid_nodes_exist(df, db_path):
    """
    Check all CSV grid_node_id values exist in db
    """
    csv_ids = set(df["grid_node_id"].astype(str).str.strip())
    db_ids = get_database_grid_node_ids(db_path)
    missing_ids = sorted(csv_ids - db_ids)

    if missing_ids:
        raise ValueError(
            f"The following grid_node_id values are not in the database: {missing_ids}"
        )
    print("All CSV grid_node_id values exist in the database.")


def validate_duplicate_grid_nodes(df):
    """
    Check for duplicate grid_node_id entries in CSV
    """
    duplicates = df[df.duplicated(subset=["grid_node_id"], keep=False)]

    if not duplicates.empty:
        raise ValueError(
            f"Duplicate grid_node_id values found:\n"
            f"{duplicates[['grid_node_id', 'grid_node_code']]}"
        )
    print("No duplicate grid_node_id values found.")


def is_valid_alt_value(value):
    """
    Check if ALT value is valid.

    Valid values are:
    - numeric values, such as 45, 62.5
    - allowed text codes, such as W, G, ND, B
    - blank values
    """
    value = str(value).strip().upper()

    if value in VALID_ALT_CODES:
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_alt_values(df):
    """
    Validate raw ALT measurement fields
    """
    alt_columns = [
        "active_layer_depth_cm_a_raw",
        "active_layer_depth_cm_b_raw",
    ]

    errors = []

    for idx, row in df.iterrows():
        for col in alt_columns:
            value = row[col]

            if not is_valid_alt_value(value):
                errors.append(
                    {
                        "row_number": idx + 2,
                        "grid_node_id": row["grid_node_id"],
                        "column": col,
                        "invalid_value": value,
                    }
                )

    if errors:
        error_df = pd.DataFrame(errors)
        raise ValueError(f"Invalid ALT values found:\n{error_df}")

    print("All ALT values are valid.")


def validate_measurement_dates(df):
    """
    Check that measurement_date values are MM/DD/YYYY
    """
    errors = []

    for idx, row in df.iterrows():
        date_value = str(row["measurement_date"]).strip()
        try:
            # Date format enforcement
            datetime.strptime(date_value, "%m/%d/%Y")
        except ValueError:
            errors.append(
                {
                    "row_number": idx + 2,
                    "grid_node_id": row["grid_node_id"],
                    "invalid_date": date_value,
                }
            )
    if errors:
        error_df = pd.DataFrame(errors)
        raise ValueError(
            "Invalid measurement_date values found.\n"
            "Dates must use MM/DD/YYYY format.\n\n"
            f"{error_df}"
        )
    print("All measurement_date values use MM/DD/YYYY format.")


def run_validation(config):
    """
    Run all CSV validation checks
    """
    csv_path = config["input_csv"]
    db_path = config["output_database"]

    print(f"Validating CSV: {csv_path}")
    print(f"Against database: {db_path}")

    df = load_csv(csv_path)

    validate_required_columns(df)
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