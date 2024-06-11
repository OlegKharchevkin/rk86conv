import wave


def open(f, mode):
    if mode == "w":
        return WavWriter(f)
    return WavReader(f)


class WavWriter:
    def __init__(self, filename, frequency=44100, write_constant=0x1d):
        self.__f = wave.open(str(filename), 'wb')
        self.__f.setnchannels(1)
        self.__f.setsampwidth(1)
        self.__f.setframerate(frequency)
        self.__writen_data = 0
        self.__writen_tacts = 0
        self.__is_closed = False
        self.__frequency = frequency
        self.__frame_time = 1 / self.__frequency
        # 4.508125e-4
        self.__tact_time = (1376 + write_constant*450)/16000000

    def write(self, data: bytes):
        frames = [b"\x20", b"\xE0"]
        time = self.__writen_data * self.__frame_time
        time -= self.__tact_time * self.__writen_tacts
        output = b""
        for byte in data:
            for j in range(8):
                bit = (byte >> (7 - j)) & 1

                x = round((self.__tact_time - time) / self.__frame_time)
                output += frames[bit] * (x // 2)
                output += frames[bit ^ 1] * ((x // 2) + (x % 2))

                self.__writen_data += x
                self.__writen_tacts += 1
                time -= self.__tact_time - x * self.__frame_time

        self.__f.writeframes(output)

    def close(self):
        if self.__is_closed:
            return
        self.__is_closed = True
        self.__f.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class WavReader:

    def __init__(self, filename, write_constant=0x1d):
        self.__f = wave.open(str(filename), 'rb')
        self.__is_closed = False

        self.__frequency = self.__f.getframerate()

        self.__halfbit_time = (1376 + write_constant*450)/32000000
        self.__time = self.__halfbit_time
        self.__readed_halfbits = 1
        self.__frame_time = 1 / self.__frequency

        self.__signed = self.__f.getsampwidth() > 1

        self.__neutral = 127 if not self.__signed else 0
        self.__max = self.__neutral
        self.__min = self.__neutral

        while int.from_bytes(self.__f.readframes(1), "little", signed=self.__signed) > self.__neutral:
            pass

        self.__flag = False
        self.__hb = 1

        while 1:
            self.__read_tact()
            if self.__flag:
                break
        if self.__read_byte() != b"\xe6":
            raise ValueError

    def __read_tact(self):
        if self.__flag:
            self.__flag = False
            return self.__hb
        count_fr = 1
        while 1:
            frame = int.from_bytes(
                self.__f.readframes(1), "little", signed=self.__signed)
            if frame > self.__neutral:
                self.__max = max(frame, self.__max)
            else:
                self.__min = min(frame, self.__min)
            self.__neutral = (self.__max + self.__min) / 2
            if (frame > self.__neutral) != self.__hb:
                count_fr += 1
                self.__time += self.__frame_time
            else:
                self.__readed_halfbits += 1
                self.__hb = (frame > self.__neutral) ^ 1
                if count_fr * self.__frame_time > 1.5 * self.__halfbit_time:
                    self.__readed_halfbits += 1
                    self.__halfbit_time = self.__time / self.__readed_halfbits
                    self.__flag = True
                    return self.__hb
                self.__halfbit_time = self.__time / self.__readed_halfbits
                return self.__hb

    def read(self, nbytes):
        ans = b""
        for i in range(nbytes):
            ans += self.__read_byte()
        return ans

    def __read_byte(self):
        byte = 0
        for i in range(8):
            self.__read_tact()
            byte = byte | (self.__hb << (7 - i))
            self.__read_tact()
        return byte.to_bytes(1)

    def close(self):
        if self.__is_closed:
            return
        self.__is_closed = True
        self.__f.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
