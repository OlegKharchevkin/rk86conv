import wave


def open(f, mode):
    """
    Open a file in specified mode.

    Args:
        f (str): The file path.
        mode (str): The mode to open the file in.

    Returns:
        WavWriter or WavReader: The opened file object.

    Raises:
        None
    """
    if mode == "w":
        # Open file in write mode.
        return WavWriter(f)
    else:
        # Open file in read mode.
        return WavReader(f)


class WavWriter:
    def __init__(self, filename: str, frequency: int = 44100, write_constant: int = 0x1d) -> None:
        """
        Initialize a WavWriter object.

        Args:
            filename (str): The path to the output file.
            frequency (int): The sample rate of the output audio. Default is 44100.
            write_constant (int): The write constant for the output audio. Default is 0x1d.

        Returns:
            None
        """
        # Open the output file in binary write mode.
        self.__f = wave.open(str(filename), 'wb')

        # Set the number of channels to 1.
        self.__f.setnchannels(1)

        # Set the sample width to 1 byte.
        self.__f.setsampwidth(1)

        # Set the sample rate to the given frequency.
        self.__f.setframerate(frequency)

        # Initialize the number of written data samples and tacts to 0.
        self.__writen_data = 0
        self.__writen_tacts = 0

        # Initialize the flag indicating whether the file is closed.
        self.__is_closed = False

        # Store the given frequency for future use.
        self.__frequency = frequency

        # Calculate the time of one frame (in seconds) based on the frequency.
        self.__frame_time = 1 / self.__frequency

        # Calculate the time of one tact (in seconds) based on the write constant.
        # 4.508125e-4
        self.__tact_time = (1376 + write_constant*450)/16000000

    def write(self, data: bytes) -> None:
        """
        Write the given bytes to the output file.

        Args:
            data (bytes): The data to write.

        Returns:
            None
        """
        # Initialize the frames to write
        frames = [b"\x20", b"\xE0"]

        # Calculate the current time in the output file
        time = self.__writen_data * self.__frame_time
        time -= self.__tact_time * self.__writen_tacts

        # Initialize the output bytearray
        output = b""

        # Iterate over each byte in the data
        for byte in data:
            # Iterate over each bit in the byte
            for j in range(8):
                # Get the bit value from the byte
                bit = (byte >> (7 - j)) & 1

                # Calculate the time of the current bit
                x = round((self.__tact_time - time) / self.__frame_time)

                # Append the appropriate frames to the output bytearray
                output += frames[bit] * (x // 2)
                output += frames[bit ^ 1] * ((x // 2) + (x % 2))

                # Update the written data and tacts
                self.__writen_data += x
                self.__writen_tacts += 1

                # Update the remaining time in the output file
                time -= self.__tact_time - x * self.__frame_time

        # Write the output bytearray to the output file
        self.__f.writeframes(output)

    def close(self) -> None:
        """
        Closes the output file and releases any system resources associated with it.

        This method is called when the WavWriter object is destroyed or when the
        close() method is called explicitly.

        Returns:
            None
        """
        # Check if the object is already closed
        if self.__is_closed:
            # If it is, do nothing and return
            return

        # Set the flag to indicate that the object is closed
        self.__is_closed = True

        # Close the output file
        self.__f.close()

    def __del__(self) -> None:
        """
        Closes the output file and releases any system resources associated with it.

        This method is called when the WavWriter object is destroyed. It ensures that the
        output file is properly closed to avoid any resource leaks.

        Returns:
            None
        """
        # Close the output file and release any system resources associated with it
        self.close()

    def __enter__(self) -> "WavWriter":
        """
        Allows the use of the WavWriter object in a context manager.

        This method is called when the WavWriter object is used in a with statement.
        It returns the WavWriter object itself, allowing the user to access its methods
        and attributes within the with block.

        Returns:
            WavWriter: The WavWriter object itself.
        """

        # Return the WavWriter object itself to allow its methods and attributes
        # to be accessed within the with block
        return self

    def __exit__(self, *args) -> None:
        """
        Closes the WavReader object in a context manager.

        This method is called when the WavReader object is used in a with statement.
        It ensures that the object is properly closed to avoid any resource leaks.

        Args:
            *args: Variable length argument list (not used in this method).

        Returns:
            None
        """
        # Close the WavReader object and release any system resources associated with it
        self.close()


class WavReader:
    def __init__(self, filename: str, write_constant: int = 0x1d) -> None:
        """
        Initializes a WavReader object.

        Args:
            filename (str): The name of the WAV file to read.
            write_constant (int, optional): The write constant for calculating the half-bit time.
                Defaults to 0x1d.

        Raises:
            ValueError: If the first byte read from the file is not \xe6.

        Returns:
            None
        """
        # Open the WAV file in read mode
        self.__f = wave.open(str(filename), 'rb')
        self.__is_closed = False

        # Get the sample rate of the WAV file
        self.__frequency = self.__f.getframerate()

        # Calculate the half-bit time based on the write constant
        self.__halfbit_time = (1376 + write_constant*450)/32000000
        self.__time = self.__halfbit_time
        self.__readed_halfbits = 1
        self.__frame_time = 1 / self.__frequency

        # Determine if the WAV file uses signed samples
        self.__signed = self.__f.getsampwidth() > 1

        # Initialize the neutral value based on the signedness of the samples
        self.__neutral = 127 if not self.__signed else 0
        self.__max = self.__neutral
        self.__min = self.__neutral

        # Skip any leading frames that are greater than the neutral value
        while int.from_bytes(self.__f.readframes(1), "little", signed=self.__signed) > self.__neutral:
            pass

        # Initialize flags and variables for reading tacts
        self.__flag = False
        self.__hb = 1

        # Read and process tacts until a flag is set
        while 1:
            self.__read_tact()
            if self.__flag:
                break

        # Check if the first byte read from the file is \xe6
        if self.__read_byte() != b"\xe6":
            raise ValueError

    def __read_tact(self) -> int:
        """
        Reads a tact from the WAV file.

        Returns:
            int: The value of the half-bit read (1 or 0).
        """
        # Check if a flag has been set
        if self.__flag:
            self.__flag = False
            return self.__hb

        count_fr = 1  # Counts the number of frames in the current half-bit
        while 1:
            # Read the next frame from the WAV file
            frame = int.from_bytes(
                self.__f.readframes(1), "little", signed=self.__signed)

            # Update the neutral value based on the maximum and minimum values
            if frame > self.__neutral:
                self.__max = max(frame, self.__max)
            else:
                self.__min = min(frame, self.__min)
            self.__neutral = (self.__max + self.__min) / 2

            # Check if the current frame value is different from the previous half-bit value
            if (frame > self.__neutral) != self.__hb:
                count_fr += 1
                self.__time += self.__frame_time
            else:
                # Update the number of read half-bits and the time
                self.__readed_halfbits += 1
                self.__hb = (frame > self.__neutral) ^ 1

                # check if we counted two half-bits
                if count_fr * self.__frame_time > 1.5 * self.__halfbit_time:
                    self.__readed_halfbits += 1
                    self.__flag = True

                # Update the half-bit time
                self.__halfbit_time = self.__time / self.__readed_halfbits
                return self.__hb

    def read(self, nbytes: int) -> bytes:
        """
        Reads the specified number of bytes from the WAV file.

        Args:
            nbytes (int): The number of bytes to read.

        Returns:
            bytes: The bytes read from the WAV file.
        """
        ans = b""
        for _ in range(nbytes):
            # Read a byte from the WAV file
            ans += self.__read_byte()
        return ans

    def __read_byte(self) -> bytes:
        """
        Reads a byte from the WAV file by reading individual half-bits.

        Returns:
            bytes: The read byte.
        """
        # Initialize the byte to 0
        byte = 0

        # Read each half-bit from left to right
        for i in range(8):
            # Read a half-bit and update the time
            self.__read_tact()

            # Set the i-th bit of the byte based on the half-bit value
            byte = byte | (self.__hb << (7 - i))

            # Read another half-bit and update the time
            self.__read_tact()

        # Return the read byte
        return byte.to_bytes(1)

    def close(self) -> None:
        """
        Closes the WAV file.

        This function is used to close the WAV file and release any system resources
        associated with it. It is generally not necessary to call this function, as
        the file will be automatically closed when the object is garbage collected.
        """
        # Check if the file is already closed
        if self.__is_closed:
            # Return if the file is already closed
            return

        # Set the flag indicating that the file is closed
        self.__is_closed = True

        # Close the WAV file
        self.__f.close()

    def __del__(self) -> None:
        """
        Destructor method.

        This method is automatically called when the object is about to be destroyed.
        It is used to close the WAV file and release any system resources associated
        with it. The close() method is called to ensure that the WAV file is properly
        closed.
        """
        # Close the WAV file
        self.close()

    def __enter__(self) -> "WavReader":
        """
        Context manager method for with statement.

        This method is used to support the with statement. It returns the WavReader
        object itself, which allows code to be executed within the with block.

        Returns:
            WavReader: The WavReader object itself.
        """
        # Return the WavReader object itself
        return self

    def __exit__(self, *args) -> None:
        """
        Context manager method for with statement.

        This method is used to support the with statement. It is called when the
        with block is exited, and it is responsible for closing the WAV file.

        Args:
            *args: Variable length argument list.

        Returns:
            None
        """
        # Close the WAV file
        self.close()
