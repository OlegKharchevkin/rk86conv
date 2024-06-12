from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a BasMicron WAV file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    Raises:
        ValueError: If the calculated checksum does not match the checksum in the file.
    """
    # Create a Data object to store the contents of the input file
    obj = Data()

    # Open the WAV file in read mode
    with wav_open.open(input_path, "r") as f:

        # Skip the first 4 bytes
        f.read(4)

        # Read the name from the file and store it in the Data object
        while (char := f.read(1)) != b"\x00":
            obj.name += char

        # Skip the next 2 bytes
        f.read(2)

        # Skip to the start of the data
        while f.read(1) != b"\xE6":
            pass
        f.read(4)

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

        # Read the checksum and compare it with the calculated checksum
        summ = int.from_bytes(f.read(2), "little")
        obj.calc_summ()
        if obj.summ != summ:
            raise ValueError(
                f"Checksum does not match {hex(summ)[2:].upper():0>4} {hex(obj.summ)[2:].upper():0>4}")

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data):
    """
    Write the contents of a Data object to a WAV file.

    Args:
        output_path (Path): The path to the file to write.
        obj (Data): The Data object containing the contents to write.

    Raises:
        None
    """
    # Open the WAV file for writing
    with wav_open.open(output_path, "w") as f:
        # Write the padding and the file signature
        f.write(b"\x00" * 64)
        f.write(b"\xe6\xd3\xd3\xd3\xd3")

        # Write the name of the program
        f.write(obj.name)

        # Write the padding and the filler
        f.write(b"\x00\x00\x00")
        f.write(b"\x55" * 64)

        # Write the next section signature
        f.write(b"\xe6\xd3\xd3\xd3")

        addr = 0x2201  # The address of the first line

        # Write the lines sorted by line number
        for i in sorted(obj.lines.keys()):
            # Write the line separator
            f.write(b"\x00")

            # Calculate the address of the next line
            addr += len(obj.lines[i]) + 5

            # Write the address of the line and the line number
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))

            # Write the line itself
            f.write(obj.lines[i])

        # Write the end of the file marker
        f.write(b"\x00\x00\x00")

        # Write the calculated checksum
        f.write(obj.summ.to_bytes(2, "little"))

        # Write the padding at the end of the file
        f.write(b"\x00" * 64)
