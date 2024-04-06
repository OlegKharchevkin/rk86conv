from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        while f.read(1) != b"\xe6":
            pass
        summ = int.from_bytes(f.read(2), "little")
        length = int.from_bytes(f.read(2), "little")
        while length > 0:
            line_len = int.from_bytes(f.read(1))
            length -= line_len
            if length <= 0 or line_len <= 0:
                break
            obj.lines.append(f.read(line_len - 1))
        obj.calc_summ()
        if summ != obj.summ:
            raise Exception("wrong summ")
        return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(b"\xe6")
        f.write(obj.summ.to_bytes(2, "little"))
        f.write(len(obj).to_bytes(2, "little"))
        for line in obj.lines:
            f.write((len(line) + 1).to_bytes(1))
            f.write(line)
        f.write(b"\x01")
