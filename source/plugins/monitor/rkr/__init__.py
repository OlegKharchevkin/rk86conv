from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a RKR file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    Raises:
        ValueError: If the calculated checksum does not match the checksum in the file.
    """
    # Create a Data object to store the contents of the input file
    obj = Data()

    # Open the RKR file in read binary mode
    with open(input_path, "rb") as f:
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

        # Calculate the checksum and check if it matches the checksum in the file
        if checksum != checksum_calc(obj.data):
            raise ValueError(
                f"Checksum does not match {hex(checksum)[2:].upper():0>4} {hex(checksum_calc(obj.data))[2:].upper():0>4}")

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes a Data object to a RKR file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object to write to the file.

    Raises:
        None
    """
    # Open the output file in binary write mode
    with open(output_path, "wb") as f:
        # Write the start and end addresses to the file
        f.write(obj.start.to_bytes(2))
        f.write(obj.end.to_bytes(2))

        # Write the data to the file
        f.write(obj.data)

        # Write the end of the data marker
        f.write(b"\x00\x00\x00\x00\x00\xE6")

        # Write the checksum to the file
        f.write(checksum_calc(obj.data).to_bytes(2))

