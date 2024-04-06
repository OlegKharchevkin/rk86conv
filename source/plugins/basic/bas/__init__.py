from .. import Data, to_basic, to_koi7, from_basic, from_koi7
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip().upper()
            buf = ""
            line_number = 0
            for i in line:
                if i == " " and line_number == 0:
                    line_number = int(buf)
                    obj.lines[line_number] = b""
                    buf = ""
                elif i == " ":
                    if buf in from_basic:
                        obj.lines[line_number] += from_basic[buf].to_bytes(1)
                    else:
                        for j in buf:
                            obj.lines[line_number] += to_koi7[j].to_bytes(1)
                    obj.lines[line_number] += to_koi7[" "].to_bytes(1)
                    buf = ""
                else:
                    buf += i
                    if buf in from_basic:
                        obj.lines[line_number] += from_basic[buf].to_bytes(1)
                        buf = ""
            if buf in from_basic:
                obj.lines[line_number] += from_basic[buf].to_bytes(1)
            else:
                for j in buf:
                    obj.lines[line_number] += to_koi7[j].to_bytes(1)
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
