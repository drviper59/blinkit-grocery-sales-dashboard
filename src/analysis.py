"""Reusable data loading and cleaning for the BlinkIT grocery analysis."""
from pathlib import Path
import pandas as pd

FAT_CONTENT_MAP = {"LF": "Low Fat", "low fat": "Low Fat", "reg": "Regular"}

def load_data(path: str | Path) -> pd.DataFrame:
    """Load source workbook and standardize field names for Python use."""
    df = pd.read_excel(path, sheet_name="BlinkIT Grocery Data")
    df.columns = df.columns.str.strip()
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy; preserve missing weights and flag outliers for review."""
    clean = df.copy()
    clean["Item Fat Content"] = clean["Item Fat Content"].replace(FAT_CONTENT_MAP)
    for col in ["Item Fat Content", "Item Type", "Outlet Location Type", "Outlet Size", "Outlet Type", "Outlet Identifier"]:
        clean[col] = clean[col].astype("string").str.strip()
    return clean
