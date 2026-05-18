"""
docker compose run --rm runner python /work/scripts/copy_db.py
"""

import logging
from pathlib import Path
import shutil
import sqlite3

from helpers.load_config import load_config


def copy_db(source_db, output_db):
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
    logging.info(f"Database copied to: {output}")


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

    logging.info("Database opened successfully.")
    print("Tables found:")
    for table in tables:
        # logging.info(f" - {table[0]}")
        print(f" - {table[0]}")



def run_copy_database(config):
    """
    Run database copy workflow with config values
    """
    copy_db(
        source_db=config["source_database"],
        output_db=config["output_database"]
    )
    # Verify db copy opens
    test_database_connection(config["output_database"])



if __name__ == "__main__":
    # Load config file
    config = load_config("/work/scripts/config/update_config.yaml")
