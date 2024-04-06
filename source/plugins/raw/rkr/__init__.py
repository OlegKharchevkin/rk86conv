from ..import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        obj.data = f.read()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(obj.data)
