from __future__ import annotations
import typing


class Trait:
    NAME: str = "unknown trait"
    DESCRIPTION: str = "no description"

    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
    def returnAttribute(self, attribute: str, value: int) -> int:
        return value
    def onTurnStart(self, entity: Entity) -> None:
        pass
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        """Modify damage before it is taken. Return the new damage amount."""
        return amount
    def afterDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> None:
        pass
    def beforeDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any) -> int:
        """Modify damage before it is dealt. Return the new damage amount."""
        return amount
    def afterDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any) -> None:
        pass
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        pass
    def __repr__(self) -> str:
        return f"Trait('{self.name}')"
