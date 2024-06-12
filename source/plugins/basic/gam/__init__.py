from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a GAM file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    """
    obj = Data()
    with open(input_path, "rb") as f:
        # Skip the signature
        while f.read(1) != b"\xE6":
            pass
        f.read(3)
        # Read the name and store it in the Data object
        obj.name = f.read(1)
        last = None
        while True:
            # Read the address of the next line and calculate the length of the line
            next = int.from_bytes(f.read(2), "little")

            if last is None:
                last = (next & 0xFF00) + 1

            length = next - last - 5

            if length < 1:
                break

            # Read the line number and the line itself
            line_number = int.from_bytes(f.read(2), "little")
            obj.lines[line_number] = f.read(length)

            f.read(1)
            last = next

    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Write the contents of a Data object to a GAM file.

    Args:
        output_path (Path): The path to the file to write.
        obj (Data): The Data object containing the contents to write.

    Raises:
        None
    """
    with open(output_path, "wb") as f:
        # Write the file signature
        f.write(b"\xe6\xd3\xd3\xd3")
        f.write(obj.name)
        addr = 1
        # Write the lines sorted by line number
        for i in sorted(obj.lines.keys()):
            # Calculate the address of the next line
            addr += len(obj.lines[i]) + 5
            # Write the address of the line and the line number
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))
            # Write the line itself
            f.write(obj.lines[i])
            f.write(b"\x00")  # Line separator
        # Write the padding
        f.write(b"\x00\x00\x00\x00\x00")  # End marker
