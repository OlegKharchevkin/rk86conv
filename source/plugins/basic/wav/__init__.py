from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with wav_open.open(input_path, "r") as f:
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

    return obj


def output(output_path: Path, obj: Data):
    with wav_open.open(output_path, "w") as f:
        f.write(b"\00" * 64)
        f.write(b"\xe6\xd3\xd3\xd3")
        addr = 1
        for i in sorted(obj.lines.keys()):
            f.write(b"\x00")
            addr += len(obj.lines[i]) + 5
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))
            f.write(obj.lines[i])
        f.write(b"\00" * 64)
