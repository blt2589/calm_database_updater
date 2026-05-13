import pandas as pd

VALID_ALT_CODES = {"W", "G", "ND", "B", ""}


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
