REQUIRED_COLUMNS = [
    "grid_node_id",
    "grid_node_code",
    "active_layer_depth_cm_a_raw",
    "active_layer_depth_cm_b_raw",
    "measurement_date",
    "metadata",
]

def validate_req_columns(df):
    """
    Check all required columns are present
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print("All required columns are present.")