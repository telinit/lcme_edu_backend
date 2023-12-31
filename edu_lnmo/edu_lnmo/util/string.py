import re


def email_ok(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email) is not None


def filename_ok(filename: str) -> bool:
    if isinstance(filename, str):
        return (255 > len(filename) > 0) \
            and filename not in [".", ".."] \
            and re.search(r"[\\/]", filename) is None
    else:
        return False