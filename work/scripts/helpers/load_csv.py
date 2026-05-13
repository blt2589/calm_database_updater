from pathlib import Path
import pandas as pd

def load_csv(csv_path):
    """
    Load field CSV as text
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    return pd.read_csv(path, dtype=str).fillna("")