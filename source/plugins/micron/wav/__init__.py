from . import wav_open
from .. import Data
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a wav file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    Raises:
        ValueError: If the calculated checksum does not match the checksum in the file.
    """
    # Create a Data object to store the contents of the input file
    obj = Data()
    with wav_open.open(input_path, "r") as f:
        # Read the name and store it in the Data object
        while (byte := f.read(1)) != b'\x00':
            if byte == b'\xe6':
                continue
            obj.name += byte
        # Skip to the start of the data
        while f.read(1) != b'\xE6':
            pass
        # Read the length of the data and store it in the Data object
        size = 0xffff - int.from_bytes(f.read(2), byteorder="little")
        obj.text = f.read(size)
        # Calculate the checksum and store it in the Data object
        obj.calc_summ()
        # Skip to the start of the checksum
        f.read(1)
        # Read the checksum in the file and check if it matches the checksum in the Data object
        summ = int.from_bytes(f.read(2), byteorder="little")
        if summ != obj.summ:
            raise ValueError(
                f"Checksum does not match {hex(summ)[2:].upper():0>4} {hex(obj.summ)[2:].upper():0>4}")
    return obj


def output(output_path: Path, obj: Data):
    """
    Writes a Data object to a wav file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents to write.

    Returns:
        None
    """
    # Open the output file in binary write mode
    with wav_open.open(output_path, "w") as f:
        # Write the file header (64 bytes of zeroes, then 5 bytes of 0xE6)
        f.write(b"\00" * 64)
        f.write(b"\xe6" * 5)
        # Write the name of the data
        f.write(obj.name)
        # Write 512 bytes of zeroes
        f.write(b"\00" * 512)
        # Write the data header (0xE6)
        f.write(b"\xe6")
        # Calculate and write the length of the data
        f.write((0xffff-len(obj.text)).to_bytes(2, "little"))
        # Write the data
        f.write(obj.text)
        # Write the end marker (0xFF)
        f.write(b"\xff")
        # Write the checksum
        f.write(obj.summ.to_bytes(2, byteorder="little"))
        # Write the file footer (64 bytes of zeroes)
        f.write(b"\00" * 64)
