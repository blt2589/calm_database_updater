import logging
import pandas as pd


def validate_alt_ranges(
    df,
    min_alt_cm=0,
    max_alt_cm=130,
    fail_on_warning=False
):
    """
    Check whether numeric ALT values fall within a plausible range

    Non-numeric field codes (W, G, ND, B) blanks ignored 
    they are handled by validate_alt_values().
    """

    alt_columns = [
        "active_layer_depth_cm_a_raw",
        "active_layer_depth_cm_b_raw",
    ]

    warnings = []

    for idx, row in df.iterrows():
        for col in alt_columns:
            raw_value = str(row[col]).strip()

            if raw_value == "":
                continue

            try:
                alt_value = float(raw_value)
            except ValueError:
                continue

            if alt_value < min_alt_cm or alt_value > max_alt_cm:
                warnings.append(
                    {
                        "row_number": idx + 2,
                        "grid_node_id": row["grid_node_id"],
                        "column": col,
                        "value_cm": alt_value,
                        "allowed_range_cm": f"{min_alt_cm}–{max_alt_cm}",
                    }
                )

    if warnings:
        warning_df = pd.DataFrame(warnings)

        message = (
            "ALT range warning(s) found.\n"
            "These values are outside the expected range and should be reviewed.\n\n"
            f"{warning_df}"
        )

        if fail_on_warning:
            raise ValueError(message)

        logging.warning(message)
        print(message)
        return warning_df

    logging.info("All numeric ALT values fall within the expected range.")
    print("All numeric ALT values fall within the expected range.")
    return pd.DataFrame()