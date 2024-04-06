from .. import Data, to_koi7, from_koi7
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "r") as f:
        for line in f.readlines():
            obj.lines.append(b"")
            for i in line:
                if i == "\n":
                    break
                if i == "\t":
                    i = " "
                if i not in to_koi7:
                    continue
                obj.lines[-1] += to_koi7[i].to_bytes(1)
            obj.lines[-1] += to_koi7["\n"].to_bytes(1)

    obj.calc_summ()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "w") as f:
        for line in obj.lines:
            for i in line:
                f.write(from_koi7[i])
