from __future__ import annotations
import typing

from .entity import Entity
from .interaction import Interaction
from .style import printTypewriter, enterToContinue


class Room:
    NAME: str = "unknown"
    ENEMIES: list[Entity] = []
    INTRO: str | None = None
    INTERACTIONS: list[Interaction] = []
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.enemies: list[Entity] = self.ENEMIES
        self.intro: str | None = self.INTRO
        self.interactions: list[Interaction] = self.INTERACTIONS
    def enter(self, skelebash: Skelebash) -> "Room": # type: ignore
        if self.intro:
            printTypewriter(self.intro)
            enterToContinue()
        self.onEnter(skelebash)
        return self
    def onEnter(self, skelebash: Skelebash) -> None: # type: ignore
        ...
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        for enemy in self.enemies:
            enemy.onTick(skelebash)
        for interaction in self.interactions:
            interaction.onTick(skelebash)
    def __repr__(self) -> str:
        return f"Room(\n  '{self.name}',\n  enemies={'\n'.join(['  '+line for line in repr(self.enemies).split('\n') if line.strip()]).strip()},\n  interactions={'\n'.join(['  '+line for line in repr(self.interactions).split('\n') if line.strip()]).strip()}\n)"

class PlaceholderRoom(Room):
    NAME: str = "placeholder room"
    ENEMIES: list[Entity] = []
    INTRO: str | None = None
    INTERACTIONS: list[Interaction] = []