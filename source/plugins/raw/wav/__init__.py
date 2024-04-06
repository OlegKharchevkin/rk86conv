from ..import Data
from pathlib import Path
from . import wav_open


def input(input_path: Path) -> Data:
    with wav_open.open(input_path, "r") as f:
        obj = Data()
        obj.data = f.read()
    return obj


def output(output_path: Path, obj: Data) -> None:
    with wav_open.open(output_path, "w") as f:
        f.write(b"\x00" * 64)
        f.write(b"\xE6")
        f.write(obj.data)
