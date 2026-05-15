"""
docker compose run --rm runner python /work/scripts/update_geoms.py
"""
import sqlite3

from helpers.load_config import load_config

def connect_spatialite(db_path, spatialite_extension="mod_spatialite"):
    """
    Connect to SQLite database, load SpatiaLite extension
    """
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    conn.load_extension(spatialite_extension)
    conn.enable_load_extension(False)
    return conn


def update_point_geometries(conn):
    """
    Update geometry columns from longitude and latitude
    Only tables with geometry columns are updated here
    Measurements inherit geometry through grid_node joins
    """

    sql_statements = [
        """
        UPDATE site
        SET geom = MakePoint(longitude, latitude, 4326)
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL;
        """,
        """
        UPDATE grid_node
        SET geom = MakePoint(longitude, latitude, 4326)
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL;
        """
    ]

    for sql in sql_statements:
        conn.execute(sql)
    conn.commit()

    print("Geometry columns updated.")


def verify_geometry_counts(conn):
    """
    Print simple geometry QA/QC counts
    """

    checks = {
        "site rows without geometry": """
            SELECT COUNT(*) FROM site WHERE geom IS NULL;
        """,
        "grid_node rows without geometry": """
            SELECT COUNT(*) FROM grid_node WHERE geom IS NULL;
        """,
        "ALT measurements without matching grid_node": """
            SELECT COUNT(*)
            FROM measurement m
            LEFT JOIN grid_node g
                ON m.grid_node_id = g.grid_node_id
            WHERE g.grid_node_id IS NULL;
        """
    }

    cur = conn.cursor()

    print("\nGeometry and view checks:")

    for label, sql in checks.items():
        cur.execute(sql)
        count = cur.fetchone()[0]
        print(f" - {label}: {count}")




def run_update_geometries_and_views(config):
    """
    Run geometry refresh and view recreation workflow
    """
    db_path = config["output_database"]
    spatialite_extension = config.get("spatialite_extension", "mod_spatialite")
    conn = connect_spatialite(db_path, spatialite_extension)

    try:
        update_point_geometries(conn)
        # recreate_measurement_views(conn)
        # recreate_latest_alt_view(conn)
        verify_geometry_counts(conn)
        print("\nGeometry and view update completed successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    config = load_config("/work/scripts/config/update_config.yaml")
    run_update_geometries_and_views(config)