from __future__ import annotations

from .entity import Player
from .item import colorBuff


class Character:
    NAME: str = "unnamed character"
    DESCRIPTION: str = "no description provided."
    STATS: list[str] = []
    ENTITY: type[Player] = Player
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.stats: list[str] = self.STATS
        self.entity: type[Player] = self.ENTITY
    def showInfo(self) -> None:
        printPanel(f"{Style.BOLD}{self.name}{Style.RESET}\n{self.description}\n* {'\n* '.join([colorBuff(stat) for stat in self.stats])}")
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(\n  '{self.name}',\n  entity={'\n'.join(['  '+line for line in repr(self.entity).split('\n') if line.strip()]).strip()})"

class Balanced(Character):
    NAME: str = "balanced"
    DESCRIPTION: str = "a balanced character with average stats."
    STATS: list[str] = [
        "starts with 100/100hp",
        "starts with 100/100st",
        "starts with 0/0mn",
        "starts with 'basic' stance"
    ]
    ENTITY: type[Player] = Player

BASE_CHARACTER_LIST: list[Character] = [Balanced()]