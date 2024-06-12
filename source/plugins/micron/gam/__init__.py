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
    # Create a Data object to store the contents of the input file
    obj = Data()
    with open(input_path, "rb") as f:
        # Find the start of the name
        while f.read(1) != b'\xE6':
            pass
        # Read the name and store it in the Data object
        while (byte := f.read(1)) != b'\x00':
            if byte == b'\xE6':
                continue
            obj.name += byte
        # Find the start of the data
        while f.read(1) != b'\xE6':
            pass
        # Read the length of the data
        size = 0xffff - int.from_bytes(f.read(2), byteorder="little")
        # Read the data and store it in the Data object
        obj.text = f.read(size)
        # Calculate the checksum and store it in the Data object
        obj.calc_summ()
        f.read(1)
        # Read the checksum in the file and check if it matches the checksum in the Data object
        summ = int.from_bytes(f.read(2), byteorder="little")
        if summ != obj.summ:
            raise ValueError(
                f"Checksum does not match {hex(summ)[2:].upper():0>4} {hex(obj.summ)[2:].upper():0>4}")
    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the contents of a Data object to a Gam file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents to write.

    Returns:
        None
    """
    # Open the output file in binary write mode
    with open(output_path, "wb") as f:
        # Write the file header
        f.write(b"\xE6\xE6\xE6\xE6\xE6")
        # Write the name
        f.write(obj.name)
        # Write the filler bytes
        f.write(b"\x00" * 64)
        # Write the data header
        f.write(b"\xE6")
        # Calculate and write the length of the data
        f.write((0xffff - len(obj.text)).to_bytes(2, byteorder="little"))
        # Write the data
        f.write(obj.text)
        # Write the end marker
        f.write(b"\xFF")
        # Write the checksum
        f.write(obj.summ.to_bytes(2, byteorder="little"))
