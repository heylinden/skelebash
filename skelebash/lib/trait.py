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

@public
class AdaptableTrait(Trait):
    NAME: str = "adaptable"
    DESCRIPTION: str = "Jack of All Trades. Gains +2% strength on dealing damage, and +2% defense on taking damage."
    def afterDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any = DamageSource.UNKNOWN) -> None:
        entity.strength_pct += 2
        printTypewriter(f"{Style.BRIGHT_GREEN}* {entity.name} adapted! strength +2% ({entity.strength_pct}% total){Style.RESET}")

    def afterDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> None:
        if amount > 0:
            entity.defense_pct += 2
            printTypewriter(f"{Style.BRIGHT_GREEN}* {entity.name} adapted! defense +2% ({entity.defense_pct}% total){Style.RESET}")

@public
class BerserkerTrait(Trait):
    NAME: str = "bloodlust"
    DESCRIPTION: str = "Damage dealt increases significantly based on missing health percentage."
    def beforeDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any = DamageSource.UNKNOWN) -> int:
        missing_hp_pct = max(0, 100 - max(0, int((entity.hp / entity.max_hp) * 100)))
        if missing_hp_pct > 0:
            printTypewriter(f"{Style.RED}{Style.BOLD}* bloodlust increases damage by {missing_hp_pct}%!{Style.RESET}")
            amount = incrpct(amount, missing_hp_pct)
        return amount

@public
class ShadowStepTrait(Trait):
    NAME: str = "shadow step"
    DESCRIPTION: str = "Instantly counter-attacks with a punch whenever an enemy attack misses/whiffs."
    def afterDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> None:
        from skelebash.lib.skill import Punch
        from skelebash.lib.damagesource import DamageSource
        if isinstance(source, tuple) and source[0] == DamageSource.SKILL:
            used = source[1]
            if used.whiffed:
                printTypewriter(f"{Style.BRIGHT_BLACK}{Style.BOLD}* {entity.name} shadow steps into the opening and counters!{Style.RESET}")
                Punch().use(entity, used.entity)

@public
class ManaShieldTrait(Trait):
    NAME: str = "mana shield"
    DESCRIPTION: str = "Consumes 15 Mana to negate 75% of incoming physical damage if enough Mana is available."
    def beforeDamageTaken(self, entity: Entity, amount: int, source: typing.Any) -> int:
        if amount > 0 and entity.mn >= 15:
            entity.mn -= 15
            reduction = min(amount, math.floor(amount * 0.75))
            amount -= reduction
            printTypewriter(f"{Style.BRIGHT_BLUE}{Style.BOLD}* {entity.name}'s mana shield absorbs {reduction} damage! (-15 MN){Style.RESET}")
        return amount