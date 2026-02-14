import re

POSTGRES_REGEX = re.compile(
    r"^postgres(ql)?(\+[a-z0-9_]+)?://",
    re.IGNORECASE
)

GENERIC_SQL_REGEX = re.compile(r"^(mysql|mariadb|sqlite|mssql|oracle)://", re.IGNORECASE)
