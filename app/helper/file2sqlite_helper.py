from pathlib import Path
import sqlite3
import pandas as pd
from app.nodes.extract_node import extract_table

def _load_tabular_file(file_path: str) -> tuple[pd.DataFrame, Path]:
    """
    Load CSV or Excel file into a DataFrame and determine SQLite path.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in {".xls", ".xlsx"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported tabular file format")

    return df, path.with_suffix(".db")


def _load_image_table(file_path: str) -> tuple[pd.DataFrame, Path]:
    """
    Extract tabular data from an image and convert it into a DataFrame.
    """
    extracted = extract_table(file_path).get("structured")

    if not extracted:
        raise ValueError("No structured data extracted from image")

    columns = extracted.get("columns")
    rows = extracted.get("rows")

    if not columns or not rows:
        raise ValueError("Extracted image table is empty")

    df = pd.DataFrame(rows, columns=columns)
    return df, Path(file_path).with_suffix(".db")


def _write_dataframe_to_sqlite(
    df: pd.DataFrame,
    sqlite_path: Path,
    table_name: str,
) -> None:
    """
    Persist a DataFrame into a SQLite database.
    """
    with sqlite3.connect(sqlite_path) as connection:
        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )
