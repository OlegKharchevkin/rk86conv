from . import asm_data as ad


def parse_number(num: str) -> int:
    """
    Parse a string representing a number and return its integer value.

    Args:
        num (str): The string to be parsed.

    Returns:
        int: The parsed integer value.

    Raises:
        ValueError: If the input string is not a valid number.
    """
    # Initialize the answer to 0
    ans = 0

    # Check if the input is a valid number
    if not is_number(num):
        raise ValueError(f"Invalid number: {num}")

    # Check if the number is in hexadecimal format
    if num.endswith("H"):
        # Convert the number from hexadecimal to decimal
        ans = int(num[:-1], base=16)
    else:
        # Convert the number from decimal to integer
        ans = int(num)

    # Return the parsed number
    return ans

def parse_line(line: str) -> list[str]:
    """
    Parse a line of assembly code and return a list of words.

    Args:
        line (str): The line of assembly code to parse.

    Returns:
        list[str]: A list of words parsed from the input line.
    """
    # Remove leading and trailing whitespace and convert to uppercase
    line = line.strip().upper()

    # Remove comments (everything after a semicolon)
    if ";" in line:
        line = line[:line.index(";")]

    # Parse the line into words
    ans = []
    buff = ''
    is_string = False
    for char in line:
        # Append characters to the buffer until a delimiter is encountered
        if is_string and char != "'":
            buff += char
        # End of string, append to answer and reset buff
        elif is_string:
            is_string = False
            ans.append(f"'{buff}'")
            buff = ''
        # Start of string, set is_string flag
        elif char == "'":
            is_string = True
        # Delimiter, append buffer to answer and reset buff
        elif char in (" ", "\t", ","):
            if buff != '':
                ans.append(buff)
                buff = ''
        # Append character to buffer
        else:
            buff += char

    # Append any remaining buffer to answer
    if buff != "":
        ans.append(buff)
        buff = ''

    return ans


def parse_db(line: list[str]) -> bytes:
    """
    Parse a line of assembly code containing DB statements and return the corresponding bytes.

    Args:
        line (list[str]): A list of words representing the DB statements.

    Returns:
        bytes: The bytes resulting from the DB statements.
    """
    ans = bytes()

    # Iterate over each word in the line
    for word in line:

        # If the word is a string, convert each character to its corresponding byte in KOI7 encoding
        if word[0] == "'":
            word = word[1:-1]
            for char in word:
                ans += ad.koi7[char]
        # Otherwise, parse the word as a number and append its corresponding byte
        else:
            ans += parse_number(word).to_bytes(1)
    return ans


def is_number(word: str) -> bool:
    """
    Check if a word represents a valid number.

    Args:
        word (str): The word to be checked.

    Returns:
        bool: True if the word is a valid number, False otherwise.
    """
    # Check if the word ends with 'H' indicating a hexadecimal number
    if word[-1] == "H":
        # Iterate over each character in the word excluding the last one
        for char in word[:-1]:
            # If any character is not a valid hexadecimal digit, return False
            if char not in "0123456789ABCDEF":
                return False
        # All characters are valid hexadecimal digits, return True
        return True
    # If the word does not end with 'H', it is assumed to be a decimal number
    else:
        # Iterate over each character in the word
        for char in word:
            # If any character is not a valid decimal digit, return False
            if char not in "0123456789":
                return False
        # All characters are valid decimal digits, return True
        return True



def is_string(word: str) -> bool:
    """
    Check if a word represents a valid string.

    Args:
        word (str): The word to be checked.

    Returns:
        bool: True if the word is a valid string, False otherwise.
    """
    # Check if the word starts and ends with a single quote
    # and is not empty
    return word[0] == "'" and word[-1] == "'" and len(word) > 2



def rp_d16(code: bytes, args: list[str]) -> bytes:
    code = (int.from_bytes(code) | (ad.rp_codes[args[0]] << 4)).to_bytes(1)
    return code + parse_number(args[1]).to_bytes(2, byteorder="little")


def rp(code: bytes, args: list[str]) -> bytes:
    return (int.from_bytes(code) | (ad.rp_codes[args[0]] << 4)).to_bytes(1)


def d16(code: bytes, args: list[str]) -> bytes:
    return code + parse_number(args[0]).to_bytes(2, byteorder="little")


def r3(code: bytes, args: list[str]) -> bytes:
    return (int.from_bytes(code) | (ad.r_codes[args[0]] << 3)).to_bytes(1)


def r3_r(code: bytes, args: list[str]) -> bytes:
    return (int.from_bytes(code) | (ad.r_codes[args[0]] << 3) | ad.r_codes[args[1]]).to_bytes(1)


def r3_d8(code: bytes, args: list[str]) -> bytes:
    code = (int.from_bytes(code) | (ad.r_codes[args[0]] << 3)).to_bytes(1)
    return code + parse_number(args[1]).to_bytes(1)


def r(code: bytes, args: list[str]) -> bytes:
    return (int.from_bytes(code) | ad.r_codes[args[0]]).to_bytes(1)


def d8(code: bytes, args: list[str]) -> bytes:
    return code + parse_number(args[0]).to_bytes(1)


def rst(code: bytes, args: list[str]) -> bytes:
    return (int.from_bytes(code) | (int(args[0]) << 3)).to_bytes(1)
