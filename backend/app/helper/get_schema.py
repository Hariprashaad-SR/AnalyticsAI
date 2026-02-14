from sqlalchemy import create_engine, text
import pandas as pd

def get_schema(DB_URL):
    """
    Dynamically fetch database schema from PostgreSQL, MySQL, or SQLite.

    Returns:
        str: LLM-friendly schema description.
    """
    engine = create_engine(DB_URL)
    schema_text = []

    with engine.connect() as conn:
        dialect = engine.dialect.name

        if dialect == "postgresql":
            query = text("""
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)
            result = conn.execute(query)

            tables = {}
            for table, column, dtype in result:
                tables.setdefault(table, []).append(f"  - {column} ({dtype})")

        elif dialect == "mysql":
            query = text("""
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                ORDER BY table_name, ordinal_position;
            """)
            result = conn.execute(query)

            tables = {}
            for table, column, dtype in result:
                tables.setdefault(table, []).append(f"  - {column} ({dtype})")

        elif dialect == "sqlite":
            tables = {}

            table_query = text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """)
            table_names = [row[0] for row in conn.execute(table_query)]

            for table in table_names:
                pragma_query = text(f"PRAGMA table_info({table});")
                columns = conn.execute(pragma_query).fetchall()

                tables[table] = [
                    f"  - {col.name} ({col.type})" for col in columns
                ]

        else:
            raise ValueError(f"Unsupported database dialect: {dialect}")

        for table, columns in tables.items():
            schema_text.append(f"TABLE: {table}")
            schema_text.extend(columns)
            schema_text.append("")

    return "\n".join(schema_text).strip()


def get_schema_csv(file_path: str) -> dict:
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, nrows=50)
    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path, nrows=50)
    else:
        raise ValueError("Unsupported file type")

    return {
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }


def columns_dict_to_text(schema_dict: dict, table_name: str = "data") -> str:
    """
    Convert column dictionary into SQL-like text schema
    """

    lines = [f"TABLE: {table_name}"]

    for column, dtype in schema_dict.get("columns", {}).items():
        lines.append(f"  - {column} ({dtype})")

    return "\n".join(lines)


