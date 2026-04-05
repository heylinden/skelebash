from __future__ import annotations
import typing

from .style import printTypewriter, Style
from .util import pct, incrpct, decrpct, public
from .damagesource import DamageSource


if typing.TYPE_CHECKING:
    from .entity import Entity

class Effect:
    NAME: str = "unknown effect"
    DESCRIPTION: str = "no description"
    SHOW: bool = True
    APPLY_MESSAGE: str = "* {entity} was afflicted with {effect}!"
    REMOVE_MESSAGE: str = "* {entity} recovered from {effect}."

    def __init__(self, level: int, duration: int = 1) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.level: int = level
        self.duration: int = duration
        self.max_duration: int = duration
        self.boost_type: str = "all" # default
    def returnAttribute(self, attribute: str, value: int) -> int:
        return value
    @classmethod
    def apply(cls, entity: Entity, level: int = 1, duration: int = 1) -> "Effect":
        effect: cls = cls(level, duration)
        entity.addEffect(effect)
        return effect
    def onApply(self, entity: Entity) -> None:
        printTypewriter(self.APPLY_MESSAGE.format(entity=entity.name, effect=self.name, duration=self.duration, **Style.__dict__))
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        self.duration -= 1
    def onRemove(self, entity: Entity) -> None:
        printTypewriter(self.REMOVE_MESSAGE.format(entity=entity.name, effect=self.name, **Style.__dict__))
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

@public
class DamageEffect(Effect):
    NAME: str = "base_damage_effect"
    DESCRIPTION: str = "takes {level} damage per turn"
    SHOW: bool = True
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None:  # type: ignore
        entity.hp -= self.level
        printTypewriter(f"{entity.name} took {self.level} damage from {self.name}! ({entity.hp} / {entity.calculate('max_hp')})")
        super().onTick(entity, skelebash)

@public
class PoisonEffect(DamageEffect):
    NAME: str = "poison"
    DESCRIPTION: str = "takes {level} poison damage per turn."
    APPLY_MESSAGE: str = "* {entity} was poisoned!"
    REMOVE_MESSAGE: str = "* {entity} is no longer poisoned."
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        printTypewriter(f"{Style.BRIGHT_GREEN}* {entity.name} suffers from poison!{Style.RESET}")
        super().onTick(entity, skelebash)

@public
class HyperarmorEffect(Effect):
    NAME: str = "hyperarmor"
    DESCRIPTION: str = "increases damage taken when interrupted during hyperarmor."
    SHOW: bool = False
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        return pct(incrpct(amount, entity.calculate("hyperarmor_strength_pct")), decrpct(100, entity.calculate("hyperarmor_defense_pct")))

@public
class ArtAmplifiedEffect(Effect):
    NAME: str = "art amplified"
    DESCRIPTION: str = "art skills used have increased stats."
    SHOW: bool = True

    def beforeDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any) -> int:
        from .skillset import Art
        if isinstance(source, tuple) and source[0] == DamageSource.SKILL:
            used = source[1]
            if any(isinstance(s, used.skill.__class__) for s in entity.art.skills):
                if self.boost_type in ["damage", "ultimate", "all"]:
                    printTypewriter(f"{Style.BRIGHT_BLUE}{Style.BOLD}* amplification active! (+100% damage){Style.RESET}")
                    amount = incrpct(amount, 100)
                used.crit = True 
        return amount

    def returnAttribute(self, attribute: str, value: int) -> int:
        if self.boost_type in ["precision", "all"] and attribute == "precision_pct":
            return value + 50
        if self.boost_type in ["critical", "all"] and attribute == "force_pct":
            return value + 100
        return value

    def afterDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any) -> None:
        from .skillset import Art
        if isinstance(source, tuple) and source[0] == DamageSource.SKILL:
            used = source[1]
            if any(isinstance(s, used.skill.__class__) for s in entity.art.skills):
                entity.removeEffect(self)

@public
class RageEffect(Effect):
    NAME: str = "rage"
    DESCRIPTION: str = "increases damage dealt by 50%, but also increases damage taken by 25%."
    SHOW: bool = True
    def beforeDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any) -> int:
        return incrpct(amount, 50)
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        return incrpct(amount, 25)

@public
class BurstEffect(Effect):
    NAME: str = "burst i-frames"
    DESCRIPTION: str = "provides i-frames for the turn."
    SHOW: bool = False
    def onApply(self, entity: Entity) -> None:
        entity.iframes = True
    def onRemove(self, entity: Entity) -> None:
        entity.iframes = False

@public
class TauntEffect(Effect):
    NAME: str = "taunted"
    DESCRIPTION: str = "doubles super gain but increases damage taken by 50%."
    SHOW: bool = True
    APPLY_MESSAGE: str = "* {entity} now gains 2x {REDDISH_PINK}super{RESET} for {duration} turns, but the target will deal 150% {BRIGHT_RED}damage{RESET}!"
    def returnAttribute(self, attribute: str, value: int) -> int:
        if attribute == "super_gain_pct":
            return value * 2
        return value
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        return incrpct(amount, 50)

@public
class GlassShieldEffect(Effect):
    NAME: str = "glass shield"
    DESCRIPTION: str = "protects from the next instance of damage."
    APPLY_MESSAGE: str = "* {entity} created a {Style.BRIGHT_BLUE}glass shield{Style.RESET}!"
    REMOVE_MESSAGE: str = "* the {Style.BRIGHT_BLUE}glass shield{Style.RESET} shattered!"
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        if amount > 0:
            printTypewriter(f"{Style.BRIGHT_BLUE}* the glass shield absorbed the impact!{Style.RESET}")
            entity.removeEffect(self)
            return 0
        return amount

@public
class OverchargeEffect(RageEffect):
    NAME: str = "overcharge"
    DESCRIPTION: str = "massively increases power and provides infinite charge."
    APPLY_MESSAGE: str = "* {entity} is OVERCHARGED!"
    REMOVE_MESSAGE: str = "* {entity} powered down."
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        entity.st = entity.calculate("max_st")
        super().onTick(entity, skelebash)