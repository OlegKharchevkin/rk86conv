from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a Basic WAV file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.
    """
    # Create an empty Data object
    obj = Data()

    # Open the WAV file in read mode
    with wav_open.open(input_path, "r") as f:
        # Skip the signature
        f.read(3)

        # Read the name and store it in the Data object
        obj.name = f.read(1)

        # Variable to keep track of the last line's address
        last = None

        # Read each line until there are no more lines
        while True:
            # Read the address of the next line and calculate the length of the line
            next = int.from_bytes(f.read(2), "little")

            # Calculate the last line's address
            if last is None:
                last = (next & 0xFF00) + 1

            length = next - last - 5

            # If the length is less than 1, break the loop
            if length < 1:
                break

            # Read the line number and the line itself
            line_number = int.from_bytes(f.read(2), "little")
            obj.lines[line_number] = f.read(length)

            # Skip the next byte
            f.read(1)

            # Update the last line's address
            last = next

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
        f.write(b"\00" * 64)
        f.write(b"\xe6\xd3\xd3\xd3")

        # Write the name of the program
        f.write(obj.name)

        # Variable to keep track of the next line's address
        addr = 1

        # Write each line sorted by line number
        for i in sorted(obj.lines.keys()):
            # Calculate the address of the next line
            addr += len(obj.lines[i]) + 5

            # Write the address of the line and the line number
            f.write(addr.to_bytes(2, "little"))
            f.write(i.to_bytes(2, "little"))

            # Write the line itself
            f.write(obj.lines[i])

            # Write the line separator
            f.write(b"\x00")

        # Write the padding
        f.write(b"\00" * 64)
