from langsmith import traceable
from app.helper.file2sqlite_helper import _load_tabular_file, _load_image_table, _write_dataframe_to_sqlite
from app.models.model import GlobalState

@traceable(name="file2sqlite")
def file_to_sqlite(state: GlobalState) -> GlobalState:
    """
    Converts supported file types (CSV, Excel, Image tables) into a SQLite database
    and updates the state to point to the generated SQL database.
    """

    file_type = state.get("file_type")
    uploaded_file = state.get("uploaded_file")

    if not uploaded_file or not file_type:
        return state

    try:
        if file_type in {"csv", "excel"}:
            df, sqlite_path = _load_tabular_file(uploaded_file)

        elif file_type == "image":
            df, sqlite_path = _load_image_table(uploaded_file)

        else:
            return state

        table_name = "data"
        _write_dataframe_to_sqlite(df, sqlite_path, table_name)

        state.update(
            {
                "uploaded_file": f"sqlite:///{sqlite_path.resolve()}",
                "file_type": "sqlDB",
                "table_name": table_name,
            }
        )

        return state

    except Exception:
        return state
