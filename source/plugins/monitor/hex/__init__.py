from .. import Data, checksum_calc
from pathlib import Path


def input(input_path: Path) -> Data:
    """
    Reads a Hex file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.

    Raises:
        ValueError: If the calculated checksum does not match the checksum in the file.
    """
    obj = Data()
    with open(input_path, "r") as f:
        # Read all lines from the file
        raw_data = [[*i.split()] for i in f.readlines()]
        # The first line contains the start address
        obj.start = int(raw_data[0][0], 16)
        # Iterate over the lines
        for i in raw_data:
            line = bytes()
            # Iterate over the hex values in the line
            for j in i[1:]:
                # If the value is 4 characters long, it is the checksum
                if len(j) == 4:
                    checksum = int(j, 16)
                    # Check if the calculated checksum matches the one in the file
                    if checksum != checksum_calc(line):
                        raise ValueError(
                            f"Checksum does not match\n{' '.join(i)} {hex(checksum_calc(line))[2:].upper():0>4}")
                else:
                    # Convert the hex value to bytes and append it to the line
                    line += int(j, 16).to_bytes(1)
            # Append the line to the Data object
            obj.data += line
    # Calculate the end address of the Data object
    obj.calc_end()
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the contents of the Data object to a Hex file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents.

    """
    with open(output_path, "w") as f:
        # Iterate over each line in the Data object
        for i in range(0, len(obj.data), 16):
            # Write the start address of the line
            f.write(f"{hex(obj.start + i)[2:]:0>4} ".upper())

            # Get the line of data
            line = obj.data[i:i+16]

            # Iterate over each byte in the line
            for j in line:
                # Write the hex value of the byte
                f.write(f"{hex(int.from_bytes(j))[2:]:0>2} ".upper())

            # Calculate and write the checksum of the line
            f.write(
                f"{hex(checksum_calc(line))[2:]:0>4}\n".upper())
