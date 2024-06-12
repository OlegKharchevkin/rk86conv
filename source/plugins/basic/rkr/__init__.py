from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a Basic RKR file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.
    """
    obj = Data()  # Create an empty Data object
    with open(input_path, "rb") as f:
        f.read(3)  # Skip the signature
        obj.name = f.read(1)  # Read the name and store it in the Data object
        last = None
        while True:
            # Read the address of the next line
            next = int.from_bytes(f.read(2), "little")

            if last is None:
                last = (next & 0xFF00) + 1

            length = next - last - 5  # Calculate the length of the line

            if length < 1:
                break

            line_number = int.from_bytes(
                f.read(2), "little")  # Read the line number
            obj.lines[line_number] = f.read(length)  # Read the line itself

            f.read(1)
            last = next

    return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(b"\xd3\xd3\xd3")
        f.write(obj.name)
        addr = 1
        for i in sorted(obj.lines.keys()):
            addr += len(obj.lines[i]) + 5
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))
            f.write(obj.lines[i])
            f.write(b"\x00")
        f.write(b"\x00\x00\x00\x00\x00")
