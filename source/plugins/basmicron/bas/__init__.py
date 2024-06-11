from .. import Data, to_basic, to_koi7, from_basic, from_koi7
from pathlib import Path


def get_line(line: str) -> bytes:
    if "\"" in line:
        a, b, c = line.split("\"", 2)
        buf = to_koi7["\""].to_bytes(1)
        for j in b.upper():
            if j in to_koi7:
                buf += to_koi7[j].to_bytes(1)
        buf += to_koi7["\""].to_bytes(1)
        return get_line(a) + buf + get_line(c)
    for i in sorted(from_basic, key=len, reverse=True):
        if i in line:
            if i == "-":
                index = line.index(i)
                for j in line[index-1::-1]:
                    if j in (" "):
                        continue
                    if j in ("=", ",", ";"):
                        break
                    a, b = line.split(i, 1)
                    return get_line(a) + from_basic[i].to_bytes(1) + get_line(b)
                continue
            a, b = line.split(i, 1)
            return get_line(a) + from_basic[i].to_bytes(1) + get_line(b)
    buf = b""
    for c in line.upper():
        if c in to_koi7:
            buf += to_koi7[c].to_bytes(1)
    return buf


def input(input_path: Path) -> Data:
    obj = Data()
    for c in input_path.name.upper():
        if c in to_koi7:
            obj.name += to_koi7[c].to_bytes(1)
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip().upper()
            buf = ""
            line_number = 0
            num, line = line.split(" ", 1)
            line_number = int(num)
            obj.lines[line_number] = get_line(line)
    obj.calc_summ()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        for i in sorted(obj.lines.keys()):
            f.write(f"{i} ")
            for j in obj.lines[i]:
                if j in to_basic:
                    f.write(to_basic[j])
                elif j in from_koi7:
                    f.write(from_koi7[j])
            f.write("\n")
