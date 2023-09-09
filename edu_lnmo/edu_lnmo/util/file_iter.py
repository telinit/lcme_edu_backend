import collections.abc as abc
import io


class FileBlockReadIterator(abc.Iterator):
    def __init__(self, f: io.FileIO, buff_size: int = 102400):
        self.f = f
        self.buff_size = buff_size

    def __next__(self) -> bytes:
        buf = self.f.read(self.buff_size)
        if len(buf) > 0:
            return buf
        else:
            raise StopIteration()
