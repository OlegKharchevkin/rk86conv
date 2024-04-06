from . import asm_data as ad


def parse_number(num: str) -> int:
    ans = 0
    if not is_nunber(num):
        raise ValueError(f"Invalid number: {num}")
    if num.endswith("H"):
        ans = int(num[:-1], base=16)
    else:
        ans = int(num)
    return ans


def parse_line(line: str) -> list[str]:
    line = line.strip().upper()
    if ";" in line:
        line = line[:line.index(";")]
    ans = []
    buff = ''
    is_string = False
    for char in line:
        if is_string and char != "'":
            buff += char
        elif is_string:
            is_string = False
            ans.append(f"'{buff}'")
            buff = ''
        elif char == "'":
            is_string = True
        elif char in (" ", "\t", ","):
            if buff != '':
                ans.append(buff)
                buff = ''
        else:
            buff += char
    if buff != "":
        ans.append(buff)
        buff = ''
    return ans


def parse_db(line: list[str]) -> bytes:
    ans = bytes()
    for word in line:
        if word[0] == "'":
            word = word[1:-1]
            for char in word:
                ans += ad.koi7[char]
        else:
            ans += parse_number(word).to_bytes(1)
    return ans


def is_nunber(word: str) -> bool:
    if word[-1] == "H":
        for char in word[:-1]:
            if char not in "0123456789ABCDEF":
                return False
        return True
    else:
        for char in word:
            if char not in "0123456789":
                return False
        return True


def is_string(word: str) -> bool:
    return word[0] == "'" and word[-1] == "'"


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
