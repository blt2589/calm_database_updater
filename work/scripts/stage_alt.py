"""
docker compose run --rm runner python /work/scripts/stage_alt.py
"""

from datetime import datetime
import sqlite3
import pandas as pd

# from helpers.load_csv import load_csv
from helpers.load_csv_folder import load_csv_folder
from helpers.load_config import load_config


def parse_alt_value(value):
    """
    Split raw ALT values into numeric or code
    """
    raw = str(value).strip()
    if raw == "":
        return None, None
    upper = raw.upper()

    try:
        return float(raw), None
    except ValueError:
        return None, upper


def format_measurement_date(value):
    """
    Convert MM/DD/YYYY date to YYYY-MM-DD for db storage
    """

    return datetime.strptime(value.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")


# TODO: Check with AEK for best way to handle node with single measurement and gravel: 42, G
def calculate_mean_alt(value_a, value_b):
    """
    Calc mean ALT ??only?? when both measurements are numeric
    """

    if value_a is not None and value_b is not None:
        return (value_a + value_b) / 2

    return None


def create_staging_table(conn):
    """
    Create staging table for reviewed ALT 

    This table holds processed records before they are inserted into
    the final measurement table.
    """

    sql = """
    CREATE TABLE IF NOT EXISTS staging_alt_measurement (
        staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
        grid_node_id TEXT NOT NULL,
        grid_node_code TEXT,
        measurement_date DATE NOT NULL,

        active_layer_depth_cm_a_raw TEXT,
        active_layer_depth_cm_b_raw TEXT,
        active_layer_depth_cm_a_code TEXT,
        active_layer_depth_cm_b_code TEXT,
        active_layer_depth_cm_a_num NUMERIC,
        active_layer_depth_cm_b_num NUMERIC,
        active_layer_depth_cm_mean_raw TEXT,
        active_layer_depth_cm_mean_num NUMERIC,

        measurement_method TEXT,
        measurement_type TEXT,
        validation_status TEXT,
        recorded_by TEXT,
        updated_by TEXT,
        metadata TEXT,

        staged_at TEXT
    );
    """
    conn.execute(sql)
    conn.commit()


def clear_staging_table(conn):
    """
    Clear existing staging records

    Prevents accidentally mixing records from multiple update runs
    """

    conn.execute("DELETE FROM staging_alt_measurement;")
    conn.commit()


def stage_measurements(df, config, conn):
    """
    Transform CSV rows and insert them into the staging table
    """

    records = []

    measurement_method = config.get("measurement_method", "manual probing")
    measurement_type = config.get("measurement_type", "")
    validation_status = config.get("validation_status", "raw")
    recorded_by = config.get("recorded_by", "")
    updated_by = config.get("updated_by", "")

    staged_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, row in df.iterrows():
        a_raw = row["active_layer_depth_cm_a_raw"].strip()
        b_raw = row["active_layer_depth_cm_b_raw"].strip()

        a_num, a_code = parse_alt_value(a_raw)
        b_num, b_code = parse_alt_value(b_raw)

        mean_num = calculate_mean_alt(a_num, b_num)

        if mean_num is not None:
            mean_raw = str(round(mean_num, 2))
        else:
            mean_raw = ""

        record = {
            "grid_node_id": row["grid_node_id"].strip(),
            "grid_node_code": row["grid_node_code"].strip(),
            "measurement_date": format_measurement_date(row["measurement_date"]),

            "active_layer_depth_cm_a_raw": a_raw,
            "active_layer_depth_cm_b_raw": b_raw,
            "active_layer_depth_cm_a_code": a_code,
            "active_layer_depth_cm_b_code": b_code,
            "active_layer_depth_cm_a_num": a_num,
            "active_layer_depth_cm_b_num": b_num,
            "active_layer_depth_cm_mean_raw": mean_raw,
            "active_layer_depth_cm_mean_num": mean_num,

            "measurement_method": measurement_method,
            "measurement_type": measurement_type,
            "validation_status": validation_status,
            "recorded_by": recorded_by,
            "updated_by": updated_by,
            "metadata": row["metadata"].strip(),

            "staged_at": staged_at,
        }

        records.append(record)

    staged_df = pd.DataFrame(records)

    staged_df.to_sql(
        "staging_alt_measurement",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()

    print(f"Staged {len(staged_df)} ALT measurement records.")


def run_staging(config):
    """
    Main staging workflow
    """

    # csv_path = config["input_csv"]
    csv_folder = config["input_csv_folder"]
    db_path = config["output_database"]

    df = load_csv_folder(csv_folder)

    conn = sqlite3.connect(db_path)

    create_staging_table(conn)
    clear_staging_table(conn)
    stage_measurements(df, config, conn)

    conn.close()

    print("ALT measurement staging completed successfully.")


if __name__ == "__main__":
    config = load_config("/work/scripts/config/update_config.yaml")
    run_staging(config)