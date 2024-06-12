from ..import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads data from a file specified by input_path and returns it as a Data object.

    Args:
        input_path (Path): The path to the file to be read.

    Returns:
        Data: A Data object containing the data that was read from the file.
    """
    # Create a Data object to store the data
    obj = Data()

    # Open the file in binary mode and read its contents
    with open(input_path, "rb") as f:
        obj.data = f.read()

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the data from a Data object to a file specified by output_path.

    Args:
        output_path (Path): The path to the file to be written.
        obj (Data): The Data object containing the data to be written.

    Returns:
        None
    """
    # Open the file in binary write mode
    with open(output_path, "wb") as f:
        # Write the data from the Data object to the file
        f.write(obj.data)
