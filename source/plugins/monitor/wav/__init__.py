from . import wav_open
from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with wav_open.open(input_path, "r") as f:
        obj.start = int.from_bytes(f.read(2))
        obj.stop = int.from_bytes(f.read(2))
        obj.data = f.read(obj.stop - obj.start + 1)
        while f.read(1) != b'\xE6':
            pass
        checksum = int.from_bytes(f.read(2))
        if checksum != checksum_calc(obj.data):
            raise ValueError(
                f"Checksum does not match {hex(checksum)[2:].upper():0>4} {hex(checksum_calc(obj.data))[2:].upper():0>4}")
    return obj


def output(output_path: Path, obj: Data) -> None:

    with wav_open.open(output_path, "w") as f:
        f.write(b"\x00" * 64)
        f.write(b"\xe6")
        f.write(obj.start.to_bytes(2))
        f.write(obj.stop.to_bytes(2))
        f.write(obj.data)
        f.write(b"\x00" * 64)
        f.write(b"\xe6")
        checksum = checksum_calc(obj.data)
        f.write(checksum.to_bytes(2))
        f.write(b"\x00" * 64)
