from .. import Data, to_koi7, from_koi7
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a txt file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.
    """
    # Initialize an empty Data object
    obj = Data()

    # Iterate over each character in the filename
    for i in input_path.stem.upper():
        # Skip characters that are not in the koi7 encoding
        if i not in to_koi7:
            continue
        # Convert the character to koi7 encoding and add it to the name of the Data object
        obj.name += to_koi7[i].to_bytes(1)

    # Open the input file in read mode
    with open(input_path, "r", encoding="utf-8") as f:
        # Iterate over each character in the file
        for i in f.read():
            # Convert the character to koi7 encoding and add it to the text of the Data object
            obj.text += to_koi7[i.upper()].to_bytes(1)

    # Calculate the checksum of the Data object
    obj.calc_summ()

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the contents of the Data object to a txt file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents.

    """
    # Open the output file in write mode with utf-8 encoding
    with open(output_path, "w", encoding="utf-8") as f:
        # Iterate over each character in the text of the Data object
        for i in obj.text:
            # Convert the character from koi7 encoding and write it to the file
            f.write(from_koi7[i])
