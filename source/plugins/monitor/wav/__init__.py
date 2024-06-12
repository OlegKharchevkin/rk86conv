from . import wav_open
from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a WAV file and returns a Data object.

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
        # Read the start and end addresses from the file
        obj.start = int.from_bytes(f.read(2))
        obj.end = int.from_bytes(f.read(2))

        # Read the data from the file
        obj.data = f.read(obj.end - obj.start + 1)

        # Find the end of the data
        while f.read(1) != b'\xE6':
            pass

        # Read the checksum from the file
        checksum = int.from_bytes(f.read(2))

        # Check if the calculated checksum matches the checksum in the file
        if checksum != checksum_calc(obj.data):
            raise ValueError(
                f"Checksum does not match {hex(checksum)[2:].upper():0>4} {hex(checksum_calc(obj.data))[2:].upper():0>4}")

    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes a Data object to a WAV file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object to write to the file.

    Raises:
        None
    """
    # Open the WAV file in write mode
    with wav_open.open(output_path, "w") as f:
        # Write the padding to the file
        f.write(b"\x00" * 64)

        # Write the start marker to the file
        f.write(b"\xe6")

        # Write the start and end addresses to the file
        f.write(obj.start.to_bytes(2))
        f.write(obj.end.to_bytes(2))

        # Write the data to the file
        f.write(obj.data)

        # Write the padding to the file
        f.write(b"\x00" * 64)

        # Write the end marker to the file
        f.write(b"\xe6")

        # Calculate and write the checksum to the file
        checksum = checksum_calc(obj.data)
        f.write(checksum.to_bytes(2))

        # Write the padding to the file
        f.write(b"\x00" * 64)
