from ..import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads binary data from a file starting from the first occurrence of the byte
    '\xE6' and returns it as a Data object.

    Args:
        input_path (Path): The path to the input file.

    Returns:
        Data: The Data object containing the read data.
    """
    # Create a Data object to store the read data
    obj = Data()
    with open(input_path, "rb") as f:
        # Read from the file until the byte '\xE6' is encountered
        while f.read(1) != b'\xE6':
            pass

        # Read the rest of the file and store it in the Data object
        obj.data = f.read()

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the binary data stored in a Data object to a file, starting with the
    byte '\xE6'.

    Args:
        output_path (Path): The path to the output file.
        obj (Data): The Data object containing the binary data to be written.
    """
    with open(output_path, "wb") as f:
        # Write the byte '\xE6' to the start of the file
        f.write(b"\xE6")
        # Write the rest of the binary data to the file
        f.write(obj.data)
