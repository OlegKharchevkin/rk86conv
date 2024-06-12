from ..import Data
from pathlib import Path
from . import wav_open


def input(input_path: Path) -> Data:
    """
    Reads a wav file and returns its contents as Data object.

    Args:
        input_path (Path): Path to the input wav file.

    Returns:
        Data: Data object containing the wav file contents.
    """
    # Open the input wav file in read mode
    with wav_open.open(input_path, "r") as f:
        # Create a new Data object
        obj = Data()
        # Read the wav file contents and store them in the Data object
        obj.data = f.read()
    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the contents of a Data object to a wav file.

    Args:
        output_path (Path): Path to the output wav file.
        obj (Data): Data object containing the wav file contents.
    """
    # Open the output wav file in write mode
    with wav_open.open(output_path, "w") as f:
        # Write the pilot tone (64 bytes of 0x00) and the stop byte (0xE6)
        f.write(b"\x00" * 64)
        f.write(b"\xE6")
        # Write the actual wav file contents
        f.write(obj.data)
