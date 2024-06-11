from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with wav_open.open(input_path, "r") as f:
        f.read(4)
        while (char := f.read(1)) != b"\x00":
            obj.name += char
        f.read(2)

        while f.read(1) != b"\xE6":
            pass
        f.read(4)

        last = None
        while True:
            next = int.from_bytes(f.read(2), "little")

            if last is None:
                last = (next & 0xFF00) + 1

            length = next - last - 5

            if length < 1:
                break

            line_number = int.from_bytes(f.read(2), "little")

            obj.lines[line_number] = f.read(length)

            f.read(1)
            last = next
        summ = int.from_bytes(f.read(2), "little")
        obj.calc_summ()
        if obj.summ != summ:
            raise ValueError(
                f"Checksum does not match {hex(summ)[2:].upper():0>4} {hex(obj.summ)[2:].upper():0>4}")
    return obj


def output(output_path: Path, obj: Data):
    with wav_open.open(output_path, "w") as f:
        f.write(b"\x00" * 64)
        f.write(b"\xe6\xd3\xd3\xd3\xd3")
        f.write(obj.name)
        f.write(b"\x00\x00\x00")
        f.write(b"\x55" * 64)
        f.write(b"\xe6\xd3\xd3\xd3")
        addr = 0x2201
        for i in sorted(obj.lines.keys()):
            f.write(b"\x00")
            addr += len(obj.lines[i]) + 5
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))
            f.write(obj.lines[i])
        f.write(b"\x00\x00\x00")
        f.write(obj.summ.to_bytes(2, "little"))
        f.write(b"\x00" * 64)
