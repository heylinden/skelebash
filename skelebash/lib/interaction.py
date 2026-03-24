from __future__ import annotations
from .entity import Entity


class Interaction:
    COMMAND: str = "i"
    TEXT: str = "interact"
    ENABLED: bool = True
    REQUIRE_INTERACT: bool = False
    def __init__(self) -> None:
        self.command: str = self.COMMAND
        self.text: str = self.TEXT
        self.enabled: bool = self.ENABLED
        self.require_interact: bool = self.REQUIRE_INTERACT
    def onInteract(self, entity: Entity) -> None:
        pass
    def onRoomEnemiesDefeated(self, room: Room) -> None: # type: ignore
        pass