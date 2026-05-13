import sqlite3
import pandas as pd


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