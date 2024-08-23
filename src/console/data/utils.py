from typing import Any


def pad(key: str, value: Any, width: int) -> str:
    """Pad the key and value to the specified width."""
    if isinstance(value, float):
        value_str = f'{value:.2f}'
    elif isinstance(value, int):
        value_str = str(value)
    else:
        value_str = str(value)

    key_width = width - len(value_str)
    return f'{key:.<{key_width}}{value_str}'