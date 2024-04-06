from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    obj = Data()
    with wav_open.open(input_path, "r") as f:
        while (byte := f.read(1)) != b'\x00':
            if byte == b'\xe6':
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


def output(output_path: Path, obj: Data):
    with wav_open.open(output_path, "w") as f:
        f.write(b"\00" * 64)
        f.write(b"\xe6" * 5)
        f.write(obj.name)
        f.write(b"\00" * 512)
        f.write(b"\xe6")
        f.write((0xffff-len(obj.text)).to_bytes(2, "little"))
        f.write(obj.text)
        f.write(b"\xff")
        f.write(obj.summ.to_bytes(2, byteorder="little"))
        f.write(b"\00" * 64)
