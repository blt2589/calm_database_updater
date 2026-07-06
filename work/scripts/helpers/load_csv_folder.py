from pathlib import Path
import pandas as pd


def load_csv_folder(csv_folder):
    """
    Load all CSV files in a source folder and combine into single DataFrame
    """

    folder = Path(csv_folder)

    if not folder.exists():
        raise FileNotFoundError(f"CSV folder not found: {folder}")

    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder}")

    dataframes = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, dtype=str).fillna("")
        df["source_csv"] = csv_file.name
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    print(f"Loaded {len(csv_files)} CSV file(s).")
    print(f"Total rows loaded: {len(combined_df)}")

    return combined_df