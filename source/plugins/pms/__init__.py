class Data:
    lines = []
    summ = 0

    def calc_summ(self) -> None:
        """
        Calculate the checksum of the data.

        The checksum is the sum of all the bytes in the data, including the line lengths.
        The result is taken modulo 2^16.

        This function updates the 'summ' attribute of the Data object.

        Args:
            self (Data): The Data object.

        Returns:
            None
        """
        # Calculate the length of the data
        length = len(self)

        # Calculate the checksum of the data
        summ = 0
        for line in self.lines:
            for byte in line:
                summ += byte
        summ += length

        # Take the result modulo 2^16
        self.summ = summ & 0xffff

    def __len__(self) -> int:
        """
        Calculate the length of the Data object, including the line lengths and the length of the length bytes.

        Returns:
            int: The length of the Data object.
        """
        # Initialize the length variable
        length = 0

        # Loop through all lines in the Data object
        for line in self.lines:
            # Calculate the length of the line, including the length byte
            line_length = len(line) + 1

            # Add the length of the line to the total length
            length += line_length

        # Add the length of the length bytes to the total length
        length += 1

        # Return the total length
        return length


to_koi7 = {"▘": 0x01,
           "▝": 0x02,
           "▀": 0x03,
           "▗": 0x04,
           "▚": 0x05,
           "▐": 0x06,
           "▜": 0x07,
           "🧍": 0x09,
           "↑": 0x0b,
           "\n": 0x0d,
           "→": 0x0e,
           "↓": 0x0f,
           "▖": 0x10,
           "▌": 0x11,
           "▞": 0x12,
           "▛": 0x13,
           "▄": 0x14,
           "▙": 0x15,
           "▟": 0x16,
           "█": 0x17,
           "|": 0x1b,
           "—": 0x1c,
           "←": 0x1d,
           "🍏": 0x1e,
           " ": 0x20,
           "!": 0x21,
           '"': 0x22,
           "#": 0x23,
           "$": 0x24,
           "%": 0x25,
           "&": 0x26,
           "'": 0x27,
           "(": 0x28,
           ")": 0x29,
           "*": 0x2a,
           "+": 0x2b,
           ",": 0x2c,
           "-": 0x2d,
           ".": 0x2e,
           "/": 0x2f,
           "0": 0x30,
           "1": 0x31,
           "2": 0x32,
           "3": 0x33,
           "4": 0x34,
           "5": 0x35,
           "6": 0x36,
           "7": 0x37,
           "8": 0x38,
           "9": 0x39,
           ":": 0x3a,
           ";": 0x3b,
           "<": 0x3c,
           "=": 0x3d,
           ">": 0x3e,
           "?": 0x3f,
           "@": 0x40,
           "A": 0x41,
           "B": 0x42,
           "C": 0x43,
           "D": 0x44,
           "E": 0x45,
           "F": 0x46,
           "G": 0x47,
           "H": 0x48,
           "I": 0x49,
           "J": 0x4a,
           "K": 0x4b,
           "L": 0x4c,
           "M": 0x4d,
           "N": 0x4e,
           "O": 0x4f,
           "P": 0x50,
           "Q": 0x51,
           "R": 0x52,
           "S": 0x53,
           "T": 0x54,
           "U": 0x55,
           "V": 0x56,
           "W": 0x57,
           "X": 0x58,
           "Y": 0x59,
           "Z": 0x5a,
           "[": 0x5b,
           "\\": 0x5c,
           "]": 0x5d,
           "^": 0x5e,
           "_": 0x5f,
           "Ю": 0x60,
           "А": 0x61,
           "Б": 0x62,
           "Ц": 0x63,
           "Д": 0x64,
           "Е": 0x65,
           "Ф": 0x66,
           "Г": 0x67,
           "Х": 0x68,
           "И": 0x69,
           "Й": 0x6a,
           "К": 0x6b,
           "Л": 0x6c,
           "М": 0x6d,
           "Н": 0x6e,
           "О": 0x6f,
           "П": 0x70,
           "Я": 0x71,
           "Р": 0x72,
           "С": 0x73,
           "Т": 0x74,
           "У": 0x75,
           "Ж": 0x76,
           "В": 0x77,
           "Ь": 0x78,
           "Ы": 0x79,
           "З": 0x7a,
           "Ш": 0x7b,
           "Э": 0x7c,
           "Щ": 0x7d,
           "Ч": 0x7e
           }

from_koi7 = {v: k for k, v in to_koi7.items()}
