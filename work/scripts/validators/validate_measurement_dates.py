import logging
from datetime import datetime


# TODO: fail if not current year
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
    logging.info("All measurement_date values use MM/DD/YYYY format.")
