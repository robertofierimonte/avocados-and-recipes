import re
import hashlib


def clean_string(string: str) -> str:
    """Clean a string.

    Args:
        string (str): _description_

    Returns:
        str: _description_
    """
    res = re.sub(r"[^A-Za-z\s]", "", string)
    res = re.sub(r"\s", "_", res)
    return res.lower()


def hash_string(string: str, lenght: int) -> int:
    """Create an integer ID by hashing a string.

    Args:
        string (str): String to be hashed
        lenght (int): Length of the resuting ID

    Returns:
        int: Integer ID obtained by hashing the input string
    """
    return int(hashlib.sha256(string.encode("utf-8")).hexdigest(), 16) % (10**lenght)
