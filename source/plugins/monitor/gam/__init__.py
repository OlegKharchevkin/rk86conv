from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        while f.read(1) != b'\xE6':
            pass
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
    with open(output_path, "wb") as f:
        f.write(b"\xE6")
        f.write(obj.start.to_bytes(2))
        f.write(obj.stop.to_bytes(2))
        f.write(obj.data)
        f.write(b"\x00\x00\x00\x00\x00\xE6")
        f.write(checksum_calc(obj.data).to_bytes(2))
