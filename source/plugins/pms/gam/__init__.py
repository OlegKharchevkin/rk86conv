from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a Gam file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    Raises:
        ValueError: If the calculated checksum does not match the checksum in the file.
    """
    obj = Data()
    with open(input_path, "rb") as f:
        # Find the start of the data
        while f.read(1) != b"\xe6":
            pass
        # Read the checksum and length
        summ = int.from_bytes(f.read(2), "little")
        length = int.from_bytes(f.read(2), "little")
        # Read the lines and add them to the Data object
        while length > 0:
            line_len = int.from_bytes(f.read(1))
            length -= line_len
            if length <= 0 or line_len <= 0:
                break
            obj.lines.append(f.read(line_len - 1))
        # Calculate and check the checksum
        obj.calc_summ()
        if summ != obj.summ:
            raise ValueError(f"Checksum does not match {hex(summ)[2:].upper():0>4} {
                             hex(obj.summ)[2:].upper():0>4}")
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes a Data object to a Gam file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents to write.
    """
    # Open the file in binary write mode
    with open(output_path, "wb") as f:
        # Write the start marker
        f.write(b"\xe6")
        # Write the calculated checksum and length
        f.write(obj.summ.to_bytes(2, "little"))
        f.write(len(obj).to_bytes(2, "little"))
        # Write each line, including the length
        for line in obj.lines:
            f.write((len(line) + 1).to_bytes(1))
            f.write(line)
        # Write the end marker
        f.write(b"\x01")
