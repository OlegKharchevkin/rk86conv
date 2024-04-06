from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        while f.read(1) != b'\xE6':
            pass
        while (byte := f.read(1)) != b'\x00':
            if byte == b'\xE6':
                continue
            obj.name += byte
        while f.read(1) != b'\xE6':
            pass
        size = 0xffff - int.from_bytes(f.read(2), byteorder="little")
        obj.text = f.read(size)
        obj.calc_summ()
        f.read(1)
        summ = int.from_bytes(f.read(2), byteorder="little")
        if summ != obj.summ:
            raise ValueError(
                f"Checksum does not match {hex(summ)[2:].upper():0>4} {hex(obj.summ)[2:].upper():0>4}")
    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(b"\xE6\xE6\xE6\xE6\xE6")
        f.write(obj.name)
        f.write(b"\x00" * 64)
        f.write(b"\xE6")
        f.write((0xffff - len(obj.text)).to_bytes(2, byteorder="little"))
        f.write(obj.text)
        f.write(b"\xFF")
        f.write(obj.summ.to_bytes(2, byteorder="little"))
