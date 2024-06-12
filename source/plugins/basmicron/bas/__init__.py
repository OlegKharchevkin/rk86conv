from .. import Data, to_basic, to_koi7, from_basic, from_koi7
from pathlib import Path


def get_line(line: str) -> bytes:
    """
    Convert a line of text to bytes according to the BASIC encoding.

    Args:
        line (str): The line of text to convert.

    Returns:
        bytes: The converted line as bytes.
    """
    # If the line contains a double quote, handle it separately
    if "\"" in line:
        # Split the line into three parts around the double quote
        a, b, c = line.split("\"", 2)
        buf = to_koi7["\""].to_bytes(1)

        # Iterate over the part between the double quotes
        for j in b.upper():
            # If the character is in the Koi7 encoding, convert it to bytes
            if j in to_koi7:
                buf += to_koi7[j].to_bytes(1)

        # Add the closing double quote to the buffer and continue with the remaining part
        buf += to_koi7["\""].to_bytes(1)
        return get_line(a) + buf + get_line(c)

    # Iterate over the possible comands in reverse order of length
    for i in sorted(from_basic, key=len, reverse=True):
        # If the command is in the line, handle it
        if i in line:
            # If the command is a minus sign, handle it separately
            if i == "-":
                index = line.index(i)

                # Iterate over the characters before the minus sign, starting from the last one
                for j in line[index-1::-1]:
                    # If the character is a space, continue to the next one
                    if j in (" "):
                        continue

                    # If the character is a separator, break the loop
                    if j in ("=", ",", ";"):
                        break

                    # Split the line at the minus sign and convert the parts recursively
                    a, b = line.split(i, 1)
                    return get_line(a) + from_basic[i].to_bytes(1) + get_line(b)

                # If the minus sign is not binary, continue to the next one
                continue

            # Split the line at the command and convert the parts recursively
            a, b = line.split(i, 1)
            return get_line(a) + from_basic[i].to_bytes(1) + get_line(b)

    # If no command is found, convert each character to bytes
    buf = b""
    for c in line.upper():
        if c in to_koi7:
            buf += to_koi7[c].to_bytes(1)

    # Return the converted line as bytes
    return buf


def input(input_path: Path) -> Data:
    """
    Reads a Bas file and returns a Data object.

    Args:
        input_path (Path): Path to the input file.

    Returns:
        Data: Data object containing the contents of the input file.
    """
    # Create a Data object to store the contents of the input file
    obj = Data()

    # Convert the name of the file to bytes and store it in the Data object
    for c in input_path.stem.upper():
        if c in to_koi7:
            obj.name += to_koi7[c].to_bytes(1)

    # Open the input file in read mode
    with open(input_path, "r", encoding="utf-8") as f:
        # Iterate over each line in the file
        for line in f.readlines():
            line = line.strip().upper()
            buf = ""
            line_number = 0

            # Split the line at the first space and convert the line number to an integer
            num, line = line.split(" ", 1)
            line_number = int(num)

            # Convert the line to bytes and store it in the Data object
            obj.lines[line_number] = get_line(line)

    # Calculate the checksum of the Data object
    obj.calc_summ()

    # Return the Data object
    return obj


def output(output_path: Path, obj: Data) -> None:
    """
    Writes the contents of a Data object to a Bas file.

    Args:
        output_path (Path): Path to the output file.
        obj (Data): Data object containing the contents to write.

    Returns:
        None
    """
    # Open the output file in write mode
    with open(output_path, "w", encoding="utf-8") as f:
        # Iterate over each line in the Data object
        for i in sorted(obj.lines.keys()):
            # Write the line number to the file
            f.write(f"{i} ")
            # Iterate over each byte in the line
            for j in obj.lines[i]:
                # If the byte is in the Basic80 encoding, write the corresponding character
                if j in to_basic:
                    f.write(to_basic[j])
                # If the byte is in the Koi7 encoding, write the corresponding character
                elif j in from_koi7:
                    f.write(from_koi7[j])
            # Write a newline character to the file after each line
            f.write("\n")
