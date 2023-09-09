import hashlib
import random
import shutil
from pathlib import Path
import io
from typing import TextIO

from edu_lnmo.util.file_iter import FileBlockReadIterator


class UploadFileStorage(object):
    def __init__(self, root: Path | str):
        self.root = Path(root)

    def __getitem__(self, hash: str) -> Path:
        if len(hash) < 5:
            raise ValueError("Bad hash value (len < 5)")

        child = self._hash_path(hash)
        if child.exists():
            return child
        else:
            raise KeyError("File not found")

    def get_path(self, hash: str) -> Path:
        return self[hash]

    def open(self, hash: str, mode: str) -> TextIO:
        return self.get_path(hash).open(mode)

    def store(self, file: io.FileIO) -> str:
        tmp = Path(self.root, f"tmp_{random.randint(0x1000000000000000,0xFFFFFFFFFFFFFFFF)}")
        tmp_f = tmp.open(mode="wb")

        h = hashlib.sha256()

        for b in FileBlockReadIterator(file):
            h.update(b)
            tmp_f.write(b)

        tmp_f.close()

        hash = h.hexdigest()
        dst = self._hash_path(hash)

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.unlink(missing_ok=True)
        shutil.move(tmp, dst)

        return hash

    def delete(self, hash: str):
        p = self.get_path(hash)
        if p.exists():
            p.unlink(missing_ok=True)
            # TODO: Remove 2 parent path fragments if they are empty

    def _hash_path(self, hash: str) -> Path:
        return Path(self.root, hash[0:2], hash[2:4], hash[4:])