import re
import pandas as pd


FLUX_NODE_PATTERN = r"^flux\d+_t\d+_\d+$"


def validate_flux_node_ids(df):
    """
    Validate Flux format grid_node_id values
    Format:
        flux6_t1_1
        flux6_t2_14
        flux10_t3_7

    Only check rows beginning with 'flux'
    """

    errors = []

    for idx, row in df.iterrows():

        grid_node_id = str(row["grid_node_id"]).strip()

        # Only validate Flux node IDs
        if grid_node_id.lower().startswith("flux"):

            if not re.match(FLUX_NODE_PATTERN, grid_node_id):

                errors.append(
                    {
                        "row_number": idx + 2,
                        "invalid_grid_node_id": grid_node_id
                    }
                )

    if errors:

        error_df = pd.DataFrame(errors)

        raise ValueError(
            "Invalid Flux grid_node_id format detected.\n"
            "Expected format: flux#_t#_#\n\n"
            f"{error_df}"
        )

    print("Flux grid_node_id values are valid.")