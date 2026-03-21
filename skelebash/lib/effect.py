from __future__ import annotations
import typing

from .style import printTypewriter, Style
from .util import pct

if typing.TYPE_CHECKING:
    from .entity import Entity

class Effect:
    NAME: str = "unknown effect"
    DESCRIPTION: str = "no description"
    SHOW: bool = True

    def __init__(self, level: int, duration: int = 1) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.level: int = level
        self.duration: int = duration
        self.max_duration: int = duration
    def returnAttribute(self, attribute: str, value: int) -> int:
        return value
    @classmethod
    def apply(cls, entity: Entity, level: int = 1, duration: int = 1) -> "Effect":
        effect: cls = cls(level, duration)
        entity.addEffect(effect)
        return effect
    def onApply(self, entity: Entity) -> None:
        printTypewriter(f"{entity.name} was afflicted with {self.name}!")
    
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        self.duration -= 1
    def onRemove(self, entity: Entity) -> None:
        printTypewriter(f"{entity.name} recovered from {self.name}.")
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
    
    def __repr__(self) -> str:
        return f"Effect('{self.name}', duration={self.duration})"

class DamageEffect(Effect):
    NAME: str = "base_damage_effect"
    DESCRIPTION: str = "takes {level} damage per turn"
    SHOW: bool = True
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None:  # type: ignore
        entity.hp -= self.level
        printTypewriter(f"{entity.name} took {self.level} damage from {self.name}! ({entity.hp} / {entity.max_hp})")
        super().onTick(entity, skelebash)

class HyperarmorEffect(Effect):
    NAME: str = "hyperarmor"
    DESCRIPTION: str = "increases damage taken when interrupted during hyperarmor."
    SHOW: bool = False
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        return pct(pct(amount, 100 + entity.calculate("hyperarmor_strength_pct")), 100 - entity.calculate("hyperarmor_defense_pct"))