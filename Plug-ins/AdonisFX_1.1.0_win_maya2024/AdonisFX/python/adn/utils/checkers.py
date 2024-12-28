import sys
import re
import tokenize
import keyword


def is_identifier(str_value):
    """Check if the input value is a valid identifier. An identifier is an
    string that contains alphanumeric letters (a-z) and (0-9), or
    underscores (_). Also, it can not start with a number, or contain
    any spaces.

    Args:
        str_value (str): string to validate.

    Returns:
        bool: True if the input value is a valid identifier. False otherwise.
    """
    # Python 3
    if sys.version_info[0] >= 3:
        return str_value.isidentifier() and str_value.isascii()
    # Python 2
    is_valid = ((re.match(tokenize.Name + '$', str_value)
                 and not keyword.iskeyword(str_value)) and
                 all(ord(char) < 128 for char in str_value))
    return is_valid or False
