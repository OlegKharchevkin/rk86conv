from .asm_data import *
from .asm_parsers import *
from .. import Data
from pathlib import Path


def gen_labels_step(labels: dict[str, int], label: str, line: list[str], addr: int) -> tuple[int, str]:
    line_str = " ".join(line)
    if line == []:
        return addr, label
    if line[0] in directives and line[0] == "ORG":
        addr = parse_number(line[1])
        return addr, label
    if line[0][-1] == ":":
        if line[0][0] == ".":
            new_lable = label + line[0][:-1]
        else:
            new_lable = line[0][:-1]
            label = new_lable
        line = line[1:]
        labels[new_lable] = addr
    if line == []:
        pass
    elif line[0] == "EQU":
        if len(line) != 2:
            raise ValueError(f"Invalid EQU statement in line {line_str}")
        labels[new_lable] = parse_number(line[1])
    elif line[0] == "DB":
        if len(line) == 1:
            raise ValueError(f"Invalid DB statement in line {line_str}")
        addr += len(parse_db(line[1:]))
    elif line[0] == "DS":
        if len(line) != 2:
            raise ValueError(f"Invalid DS statement in line {line_str}")
        addr += parse_number(line[1])
    elif line[0] in codes:
        addr += codes[line[0]][1]
    return addr, label


def gen_codes_step(labels: dict[str, int], lable: str, line: list[str], addr: int, data: bytes) -> tuple[int, dict[str, int], bytes]:
    line_str = " ".join(line)
    if len(line) == 0:
        return addr, lable, data
    if line[0][:-1] in labels:
        lable = line[0][:-1]
        line = line[1:]
    elif lable + line[0][:-1] in labels:
        line = line[1:]
    new_line = []
    for word in line:
        if is_nunber(word):
            new_line.append(word)
        elif is_string(word):
            new_line.append(word)
        elif word[0] == ".":
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
    if line == []:
        pass
    elif line[0] == "ORG" and data == b"":
        if len(line) != 2:
            raise ValueError(f"Invalid ORG statement in line {line_str}")
        addr = parse_number(line[1])
    elif line[0] == "ORG":
        if len(line) != 2:
            raise ValueError(f"Invalid ORG statement in line {line_str}")
        data += b"\x00" * (parse_number(line[1]) - addr)
        addr = parse_number(line[1])
    elif line[0] == "EQU":
        if len(line) != 2:
            raise ValueError(f"Invalid EQU statement in line {line_str}")
        return addr, lable, data
    elif line[0] == "DB":
        if len(line) == 1:
            raise ValueError(f"Invalid DB statement in line {line_str}")
        data += parse_db(line[1:])
        addr += len(parse_db(line[1:]))
    elif line[0] == "DS":
        if len(line) != 2:
            raise ValueError(f"Invalid DS statement in line {line_str}")
        data += b"\x00" * parse_number(line[1])
        addr += parse_number(line[1])
    elif line[0] in codes:
        if line[0] not in codes:
            raise ValueError(f"Invalid code in line {line_str}")
        data += codes[line[0]][0](line[1:])
        addr += codes[line[0]][1]
    return addr, lable, data


def input(input_path: Path) -> Data:
    obj = Data()

    labels = {}
    with open(str(input_path), "r", encoding="utf-8") as f:
        addr = 0
        lable = ''
        for line in f.readlines():
            line = parse_line(line)
            addr, lable = gen_labels_step(labels, lable, line, addr)

    max_len_label = len(max(labels, key=lambda x: len(x)))
    for i in labels:
        print(
            f"{i + ':': <{max_len_label + 1}} {hex(labels[i])[2:].upper():0>4}")

    with open(str(input_path), "r", encoding="utf-8") as f:
        addr = 0
        lable = ''
        for line in f.readlines():
            line = parse_line(line)
            addr, lable, obj.data = gen_codes_step(
                labels, lable, line, addr, obj.data)
            if obj.data == b"":
                obj.start = addr
    obj.calc_stop()
    return obj


output = None
