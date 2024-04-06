from .. import Data, to_koi7, from_koi7
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    for i in input_path.stem.upper():
        if i not in to_koi7:
            continue
        obj.name += to_koi7[i].to_bytes(1)
    with open(input_path, "r", encoding="utf-8") as f:
        for i in f.read():
            obj.text += to_koi7[i.upper()].to_bytes(1)
    obj.calc_summ()
    return obj


def output(output_path: Path, obj: Data):
    with open(output_path, "w", encoding="utf-8") as f:
        for i in obj.text:
            f.write(from_koi7[i])
