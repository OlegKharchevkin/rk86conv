from .asm_data import *
from .asm_parsers import *
from .. import Data
from pathlib import Path


def gen_labels_step(labels: dict[str, int], label: str, line: list[str], addr: int) -> tuple[int, str]:
    """
    Generates labels for the given line of assembly code.

    Args:
        labels (dict[str, int]): Dictionary containing labels.
        label (str): Current label.
        line (list[str]): List of words in the line.
        addr (int): Current address.

    Returns:
        tuple[int, str]: Updated address and label.
    """
    line_str = " ".join(line)

    # If line is empty, return current address and label
    if line == []:
        return addr, label

    # If line starts with "ORG", update address and return
    if line[0] in directives and line[0] == "ORG":
        addr = parse_number(line[1])
        return addr, label

    # If line starts with label, update label
    if line[0][-1] == ":":
        # If label starts with ".", append it to current label
        if line[0][0] == ".":
            new_lable = label + line[0][:-1]
        else:
            new_lable = line[0][:-1]
            label = new_lable
        line = line[1:]
        labels[new_lable] = addr

    # If line is empty, do nothing
    if line == []:
        pass

    # If line starts with "EQU", update label value and return
    elif line[0] == "EQU":
        if len(line) != 2:
            raise ValueError(f"Invalid EQU statement in line {line_str}")
        labels[new_lable] = parse_number(line[1])

    # If line starts with "DB", update address and return
    elif line[0] == "DB":
        if len(line) == 1:
            raise ValueError(f"Invalid DB statement in line {line_str}")
        addr += len(parse_db(line[1:]))

    # If line starts with "DS", update address and return
    elif line[0] == "DS":
        if len(line) != 2:
            raise ValueError(f"Invalid DS statement in line {line_str}")
        addr += parse_number(line[1])

    # If line starts with a valid instruction, update address
    elif line[0] in codes:
        addr += codes[line[0]][1]

    return addr, label


def gen_codes_step(labels: dict[str, int], lable: str, line: list[str], addr: int, data: bytes) -> tuple[int, dict[str, int], bytes]:
    """
    Generates codes for the given line of assembly code.

    Args:
        labels (dict[str, int]): Dictionary containing labels.
        lable (str): Current label.
        line (list[str]): List of words in the line.
        addr (int): Current address.
        data (bytes): Current data.

    Returns:
        tuple[int, dict[str, int], bytes]: Updated address, labels, and data.
    """
    line_str = " ".join(line)

    # If line is empty, return current address, labels, and data
    if len(line) == 0:
        return addr, lable, data

    # If label is defined, update current label
    if line[0][:-1] in labels:
        lable = line[0][:-1]
        line = line[1:]
    # If label is not defined, try appending it to the current label
    elif lable + line[0][:-1] in labels:
        line = line[1:]

    # Replace labels with their values in the line
    new_line = []
    for word in line:
        if is_number(word):
            new_line.append(word)
        elif is_string(word):
            new_line.append(word)
        elif word[0] == ".":
            # If label is not defined, raise an error
            if (lable + word) not in labels:
                raise ValueError(
                    f"Undefined label {lable + word} in line {line_str}")
            new_line.append(str(labels[lable + word]))
        elif word in labels:
            new_line.append(str(labels[word]))
        elif word in directives or word in codes or word in r_codes or word in rp_codes:
            new_line.append(word)
        else:
            raise ValueError(f"Undefined label {word} in line {line_str}")
    line = new_line

    # If line is empty, do nothing
    if line == []:
        pass

    # If line starts with ORG, update address and data
    elif line[0] == "ORG" and data == b"":
        if len(line) != 2:
            raise ValueError(f"Invalid ORG statement in line {line_str}")
        addr = parse_number(line[1])
    elif line[0] == "ORG":
        if len(line) != 2:
            raise ValueError(f"Invalid ORG statement in line {line_str}")
        data += b"\x00" * (parse_number(line[1]) - addr)
        addr = parse_number(line[1])

    # If line starts with EQU, update labels and data
    elif line[0] == "EQU":
        if len(line) != 2:
            raise ValueError(f"Invalid EQU statement in line {line_str}")
        return addr, lable, data

    # If line starts with DB, update data and address
    elif line[0] == "DB":
        if len(line) == 1:
            raise ValueError(f"Invalid DB statement in line {line_str}")
        data += parse_db(line[1:])
        addr += len(parse_db(line[1:]))

    # If line starts with DS, update data and address
    elif line[0] == "DS":
        if len(line) != 2:
            raise ValueError(f"Invalid DS statement in line {line_str}")
        data += b"\x00" * parse_number(line[1])
        addr += parse_number(line[1])

    # If line starts with a valid instruction, update data and address
    elif line[0] in codes:
        if line[0] not in codes:
            raise ValueError(f"Invalid code in line {line_str}")
        data += codes[line[0]][0](line[1:])
        addr += codes[line[0]][1]

    return addr, lable, data


def input(input_path: Path) -> Data:
    """
    Reads a assembly language file and generates a Data object with the corresponding data.

    Args:
        input_path (Path): Path to the assembly language file.

    Returns:
        Data: Data object generated from the assembly language file.
    """

    # Create a Data object to store the data.
    obj = Data()

    # Create a dictionary to store the labels.
    labels = {}

    # Read the assembly language file and generate labels.
    with open(str(input_path), "r", encoding="utf-8") as f:
        addr = 0
        lable = ''
        for line in f.readlines():
            line = parse_line(line)
            addr, lable = gen_labels_step(labels, lable, line, addr)

    # Print the labels and their corresponding addresses.
    max_len_label = len(max(labels, key=lambda x: len(x)))
    for i in labels:
        print(
            f"{i + ':': <{max_len_label + 1}} {hex(labels[i])[2:].upper():0>4}")

    # Read the assembly language file again and generate codes.
    with open(str(input_path), "r", encoding="utf-8") as f:
        addr = 0
        lable = ''
        for line in f.readlines():
            line = parse_line(line)
            addr, lable, obj.data = gen_codes_step(
                labels, lable, line, addr, obj.data)
            if obj.data == b"":
                obj.start = addr

    # Calculate the end address of the data.
    obj.calc_end()

    # Return the generated Data object.
    return obj


output = None
