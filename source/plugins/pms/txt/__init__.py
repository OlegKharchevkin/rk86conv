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

    # Open the input file in read mode
    with open(input_path, "r") as f:

        # Iterate over each line in the file
        for line in f.readlines():

            # Initialize an empty line in the Data object
            obj.lines.append(b"")

            # Iterate over each character in the line
            for i in line:

                # If the character is a newline, break the loop
                if i == "\n":
                    break

                # If the character is a tab, replace it with a space
                if i == "\t":
                    i = " "

                # If the character is not in the koi7 encoding, skip it
                if i not in to_koi7:
                    continue

                # Convert the character to koi7 encoding and append it to the line
                obj.lines[-1] += to_koi7[i].to_bytes(1)

            # Append a newline character to the line
            obj.lines[-1] += to_koi7["\n"].to_bytes(1)

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
    with open(output_path, "w") as f:
        # Iterate over each line in the Data object
        for line in obj.lines:

            # Iterate over each character in the line
            for i in line:
                f.write(from_koi7[i])

            # Add a newline character to the end of the line
            f.write("\n")
