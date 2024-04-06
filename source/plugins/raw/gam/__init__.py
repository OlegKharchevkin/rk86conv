from ..import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        while f.read(1) != b'\xE6':
            pass
        obj.data = f.read()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(b"\xE6")
        f.write(obj.data)
