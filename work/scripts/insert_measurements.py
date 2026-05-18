"""
docker compose run --rm runner python /work/scripts/insert_measurements.py
"""

import logging
import sqlite3

from helpers.load_config import load_config


def check_staging_table_exists(conn):
    """
    Confirm staging table exists
    """
    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'staging_alt_measurement';
    """)

    result = cur.fetchone()

    if result is None:
        raise RuntimeError("staging_alt_measurement table does not exist.")

    logging.info("Staging table found.")

## TODO: if not 121 records (for grid) or 71 records (for flux), throw exception? what about 56mile (how many)?
def count_staged_records(conn):
    """
    Count staged records before insertion
    """
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM staging_alt_measurement;")
    count = cur.fetchone()[0]

    if count == 0:
        raise RuntimeError("No records found in staging_alt_measurement.")

    logging.info(f"Staged records found: {count}")

    return count


def check_for_duplicate_measurements(conn):
    """
    Check if staged measurements already exist in the measurement table

    Duplicate is identified as the same grid_node_id and measurement_date
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT
            s.grid_node_id,
            s.measurement_date
        FROM staging_alt_measurement s
        INNER JOIN measurement m
            ON s.grid_node_id = m.grid_node_id
           AND s.measurement_date = m.measurement_date;
    """)

    duplicates = cur.fetchall()

    if duplicates:
        duplicate_text = "\n".join(
            [f"{grid_node_id}, {measurement_date}" for grid_node_id, measurement_date in duplicates]
        )

        raise RuntimeError(
            "Duplicate measurements found in measurement table.\n"
            "Insertion stopped.\n\n"
            f"{duplicate_text}"
        )

    logging.info("No duplicate measurements found.")


def insert_measurements_from_staging(conn):
    """
    Insert staged ALT measurements into the measurement table

    Maps only fields that exist in the production measurement table
    """

    sql = """
        INSERT INTO measurement (
            grid_node_id,
            measurement_date,
            active_layer_depth_cm_a_raw,
            active_layer_depth_cm_b_raw,
            active_layer_depth_cm_a_code,
            active_layer_depth_cm_b_code,
            active_layer_depth_cm_a_num,
            active_layer_depth_cm_b_num,
            active_layer_depth_cm_mean_raw,
            active_layer_depth_cm_mean_num,
            snow_depth_cm,
            measurement_method,
            validation_status,
            recorded_by,
            updated_by,
            metadata
        )
        SELECT
            grid_node_id,
            measurement_date,
            active_layer_depth_cm_a_raw,
            active_layer_depth_cm_b_raw,
            active_layer_depth_cm_a_code,
            active_layer_depth_cm_b_code,
            active_layer_depth_cm_a_num,
            active_layer_depth_cm_b_num,
            active_layer_depth_cm_mean_raw,
            active_layer_depth_cm_mean_num,
            NULL AS snow_depth_cm,
            measurement_method,
            validation_status,
            recorded_by,
            updated_by,
            metadata
        FROM staging_alt_measurement;
    """

    cur = conn.cursor()
    cur.execute(sql)

    inserted_count = cur.rowcount

    conn.commit()

    logging.info(f"Inserted records into measurement table: {inserted_count}")

    return inserted_count


def run_insert(config):
    """
    Run the staged-to-prod measurement insertion
    """
    db_path = config["output_database"]

    conn = sqlite3.connect(db_path)

    try:
        check_staging_table_exists(conn)
        staged_count = count_staged_records(conn)
        check_for_duplicate_measurements(conn)

        inserted_count = insert_measurements_from_staging(conn)

        if inserted_count != staged_count:
            raise RuntimeError(
                f"Inserted count does not match staged count. "
                f"Staged: {staged_count}, Inserted: {inserted_count}"
            )

        logging.info("Measurement insertion completed successfully.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    config = load_config("/work/scripts/config/update_config.yaml")
    run_insert(config)
