from decimal import Decimal
from typing import Any


def convert_decimals(obj: Any) -> Any:
    """
    Convert Decimal values into float for JSON serialization.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj