from abc import ABC
from typing import *

D = TypeVar("D")

class DataImporter(ABC, Generic[D]):
    def do_import(self, data: D):
        pass


class CSVDataImporter(DataImporter[str]):
    def do_import(self, data: str):
        pass
