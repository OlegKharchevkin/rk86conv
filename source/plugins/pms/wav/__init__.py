from . import wav_open
from .. import Data
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
        # Read the checksum and length from the file
        summ = int.from_bytes(f.read(2), "little")
        length = int.from_bytes(f.read(2), "little")

        # Read the lines and add them to the Data object
        while length > 0:
            # Read the length of the next line
            line_len = int.from_bytes(f.read(1))
            length -= line_len

            # If the length is invalid, break the loop
            if length <= 0 or line_len <= 0:
                break

            # Read the line and add it to the Data object
            obj.lines.append(f.read(line_len - 1))

        # Calculate the checksum and check if it matches the checksum in the file
        obj.calc_summ()
        if summ != obj.summ:
            raise ValueError(f"Checksum does not match {hex(summ)[2:].upper():0>4} "
                             f"{hex(obj.summ)[2:].upper():0>4}")

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data):
    """
    Writes a Data object to a WAV file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents to write.
    """
    # Open the WAV file in write mode
    with wav_open.open(output_path, "w") as f:
        # Write the padding to the file
        f.write(b"\00" * 64)

        # Write the start marker to the file
        f.write(b"\xe6")

        # Write the checksum and length to the file
        f.write(obj.summ.to_bytes(2, "little"))
        f.write(len(obj).to_bytes(2, "little"))

        # Write each line, including the length, to the file
        for line in obj.lines:
            f.write((len(line) + 1).to_bytes(1))
            f.write(line)

        # Write the end marker to the file
        f.write(b"\x01")

        # Write the padding to the file
        f.write(b"\00" * 64)
