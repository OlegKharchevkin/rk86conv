class Data:
    data = bytes()
    start = 0
    end = 0

    def calc_end(self) -> None:
        """
        Calculate the end address of the data.

        This function calculates the end address of the data by adding the length of the data to the start address and subtracting 1.

        Returns:
            None
        """
        # Calculate the end address by adding the length of the data to the start address and subtracting 1.
        self.end = self.start + len(self.data) - 1


def checksum_calc(data: bytes) -> int:
    """
    Calculate the checksum of a byte array.

    This function calculates the checksum of a byte array by summing up the bytes in the array.

    Args:
        data (bytes): The byte array to calculate the checksum for.

    Returns:
        int: The checksum of the byte array.
    """
    # Initialize the checksum to 0
    summ = 0

    # Iterate over each byte in the data array
    for i in data:
        # Add the current byte to the checksum
        # The bitwise operations are used to shift the byte left by 8 bits and combine it with the byte itself
        summ += (i << 8) | i

    # Subtract the last byte in the array multiplied by 256 from the checksum
    summ -= int.from_bytes(data[-1:]) << 8

    # Return the checksum modulo 65536 (to ensure the checksum fits in 16 bits)
    return summ & 0xffff
