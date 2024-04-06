class Data:
    data = bytes()
    start = 0
    stop = 0

    def calc_stop(self):
        self.stop = self.start + len(self.data) - 1


def checksum_calc(data: bytes) -> int:
    summ = 0
    for i in data:
        summ += (i << 8) | i
    summ -= int.from_bytes(data[-1:]) << 8
    return summ & 0xffff
