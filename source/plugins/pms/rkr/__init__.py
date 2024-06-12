from .. import Data
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
    with open(input_path, "rb") as f:
        # Read the checksum and length
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
            raise ValueError(f"Checksum does not match {hex(summ)[2:].upper():0>4} {
                             hex(obj.summ)[2:].upper():0>4}")

        # Return the Data object
        return obj


def output(output_path: Path, obj: Data) -> None:
    with open(output_path, "wb") as f:
        f.write(obj.summ.to_bytes(2, "little"))
        f.write(len(obj).to_bytes(2, "little"))
        for line in obj.lines:
            f.write((len(line) + 1).to_bytes(1))
            f.write(line)
        f.write(b"\x01")
