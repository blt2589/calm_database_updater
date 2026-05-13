"""
docker compose run --rm runner python /work/scripts/copy_db.py
"""

from pathlib import Path
import shutil
import sqlite3
import yaml


def load_config(config_path):
    """
    Load config settings from YAML
    Parameters:
        config_path (str): Path to config YAML
    Returns:
        dict: config dictionary
    """   
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def copy_database(source_db, output_db):
    """
    Create copy of source database.
    """
    source = Path(source_db)
    output = Path(output_db)

    if not source.exists():
        raise FileNotFoundError(f"Source database not found: {source}")

    if output.exists():
        raise FileExistsError(f"Output database already exists: {output}")

    shutil.copy2(source, output)
    print(f"Database copied to: {output}")


def test_database_connection(db_path):
    """
    Open database copy and verify tables exist
    Basic integrity check
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    conn.close()

    print("Database opened successfully.")
    print("Tables found:")
    for table in tables:
        print(f" - {table[0]}")


if __name__ == "__main__":
    # Load config file
    config = load_config("/work/scripts/config/update_config.yaml")

    # Create working copy of db
    copy_database(
        source_db=config["source_database"],
        output_db=config["output_database"]
    )
    # Verify db copy opens
    test_database_connection(config["output_database"])