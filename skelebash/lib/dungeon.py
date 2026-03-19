from __future__ import annotations
from .room import Room, PlaceholderRoom


class Dungeon:
    NAME: str = "unknown"
    ROOMS: list[Room] = []
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.rooms: list[Room] = self.ROOMS
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        ...
    def __repr__(self) -> str:
        return f"Dungeon(\n  '{self.name}',\n  rooms={'\n'.join(['  '+line for line in repr(self.rooms).split('\n') if line.strip()]).strip()}\n)"

class PlaceholderDungeon(Dungeon):
    NAME: str = "placeholder dungeon"
    ROOMS: list[Room] = [PlaceholderRoom()]