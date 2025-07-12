from abc import ABC, abstractmethod
from pathlib import Path


class Seeder(ABC):
    @abstractmethod
    def truncate(self) -> None:
        pass

    @abstractmethod
    def seed(self, folder: Path) -> None:
        pass


class SeederManager:
    def __init__(self, seeders: list[Seeder]):
        self._seeders = seeders

    def truncate(self) -> None:
        for seeder in self._seeders:
            seeder.truncate()

    def seed(self, folder: Path) -> None:
        for seeder in self._seeders:
            seeder.seed(folder)
