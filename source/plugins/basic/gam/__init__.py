from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    obj = Data()
    with open(input_path, "rb") as f:
        while f.read(1) != b"\xE6":
            pass
        f.read(3)
        obj.name = f.read(1)
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


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(b"\xe6\xd3\xd3\xd3")
        f.write(obj.name)
        addr = 1
        for i in sorted(obj.lines.keys()):
            addr += len(obj.lines[i]) + 5
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))
            f.write(obj.lines[i])
            f.write(b"\x00")
        f.write(b"\x00\x00\x00\x00\x00")
