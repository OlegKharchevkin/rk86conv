from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "r") as f:
        raw_data = [[*i.split()] for i in f.readlines()]
        obj.start = int(raw_data[0][0], 16)
        for i in raw_data:
            line = bytes()
            for j in i[1:]:
                if len(j) == 4:
                    checksum = int(j, 16)
                    if checksum != checksum_calc(line):
                        raise ValueError(
                            f"Checksum does not match\n{' '.join(i)} {hex(checksum_calc(line))[2:].upper():0>4}")
                else:
                    line += int(j, 16).to_bytes(1)
            obj.data += line
    obj.calc_stop()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "w") as f:
        for i in range(0, len(obj.data), 16):
            f.write(f"{hex(obj.start + i)[2:]:0>4} ".upper())
            line = obj.data[i:i+16]
            for j in line:
                f.write(f"{hex(int.from_bytes(j))[2:]:0>2} ".upper())
            f.write(
                f"{hex(checksum_calc(line))[2:]:0>4}\n".upper())
