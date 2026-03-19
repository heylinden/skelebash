from __future__ import annotations
import typing

from .item import Item
from .itembundle import ItemBundle
from .style import Style
from .skill import Skill
from .skillset import Armament, Art, Skillset, Stance
from .effect import Effect
from .trait import Trait
from .damagesource import DamageSource
from .brain import Brain


class Entity:
    NAME: str = "unknown"
    DESCRIPTION: str = "no description"
    HP: int = 100 # hit points
    MAX_HP: int = 100
    ST: int = 100 # stamina
    MAX_ST: int = 100
    MN: int = 0 # mana
    MAX_MN: int = 0
    BH: int = 20 # block health
    MAX_BH: int = 20
    BH_RECOVERY: int = 5 # block health regenerated per turn
    STRENGTH_PCT: int = 0 # % outgoing damage increase
    DEFENSE_PCT: int = 0 # % incoming damage reduction
    PRECISION_PCT: int = 0 # % outgoing crit chance increase
    FORCE_PCT: int = 100 # % outgoing crit damage increase
    CONCENTRATION_PCT: int = 0 # % outgoing whiff chance reduction
    AGILITY_PCT: int = 0 # % incoming whiff chance increase
    DURABILITY_PCT: int = 0 # % incoming crit chance reduction
    
    BLOCK_STRENGTH_PCT: int = 0 # % outgoing damage to block increase
    BLOCK_EFFICIENCY_PCT: int = 75 # % incoming damage to block reduction

    HYPERARMOR_STRENGTH_PCT: int = 50 # % outgoing damage to hyperarmor increase
    HYPERARMOR_DEFENSE_PCT: int = 0 # % incoming damage to hyperarmor reduction

    INVENTORY: ItemBundle = ItemBundle()
    SKILLS: Skillset = Skillset()

    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.hp: int = self.HP
        self.max_hp: int = self.MAX_HP
        self.st: int = self.ST
        self.max_st: int = self.MAX_ST
        self.mn: int = self.MN
        self.max_mn: int = self.MAX_MN
        self.stun: int = 0
        self.strength_pct: int = self.STRENGTH_PCT
        self.defense_pct: int = self.DEFENSE_PCT
        self.precision_pct: int = self.PRECISION_PCT
        self.force_pct: int = self.FORCE_PCT
        self.concentration_pct: int = self.CONCENTRATION_PCT
        self.agility_pct: int = self.AGILITY_PCT
        self.durability_pct: int = self.DURABILITY_PCT
        self.block_strength_pct: int = self.BLOCK_STRENGTH_PCT
        self.block_efficiency_pct: int = self.BLOCK_EFFICIENCY_PCT
        self.hyperarmor_strength_pct: int = self.HYPERARMOR_STRENGTH_PCT
        self.hyperarmor_defense_pct: int = self.HYPERARMOR_DEFENSE_PCT
        self.inventory: ItemBundle = self.INVENTORY
        self.skills: Skillset = self.SKILLS
        self.last_skill_used: Skill.Used | None = None
        self.effects: list[Effect] = []
        self.traits: list[Trait] = []
        self.brain: Brain | None = None

    def calculate(self, attribute: str) -> int:
        value: int = getattr(self, attribute)
        for trait_or_effect in self.traits + self.effects:
            value = trait_or_effect.returnAttribute(attribute, value)
        print(attribute, value)
        return value
    def heal(self, amount: int = None) -> "Entity":
        amount = amount or self.max_hp - self.hp
        self.hp += min(amount, self.max_hp - self.hp)
        return self
    def healStamina(self, amount: int = None) -> "Entity":
        amount = amount or self.max_st - self.st
        self.st += min(amount, self.max_st - self.st)
        return self
    def healMana(self, amount: int = None) -> "Entity":
        amount = amount or self.max_mn - self.mn
        self.mn += min(amount, self.max_mn - self.mn)
        return self

    def addEffect(self, effect: Effect) -> None:
        for trait_or_effect in self.traits + self.effects:
            effect = trait_or_effect.beforeEffectApplied(self, effect)
        self.effects.append(effect)
        effect.onApply(self)
        for trait_or_effect in self.traits + self.effects:
            trait_or_effect.afterEffectApplied(self, effect)

    def removeEffect(self, effect: Effect) -> None:
        if effect in self.effects:
            effect.onRemove(self)
            self.effects.remove(effect)

    def addTrait(self, trait: Trait) -> None:
        self.traits.append(trait)

    def removeTrait(self, trait: Trait) -> None:
        if trait in self.traits:
            self.traits.remove(trait)

    def takeDamage(self, amount: int, source: typing.Any) -> int:
        for trait_or_effect in self.traits + self.effects:
            amount = trait_or_effect.beforeDamageTaken(self, amount, source)
        self.hp = max(0, self.hp - amount)
        for trait_or_effect in self.traits + self.effects:
            trait_or_effect.afterDamageTaken(self, amount, source)
        return amount

    def dealDamage(self, amount: int, target: Entity, source: DamageSource | tuple[DamageSource, typing.Any] = DamageSource.UNKNOWN) -> int:
        for trait_or_effect in self.traits + self.effects:
            amount = trait_or_effect.beforeDamageDealt(self, amount, target, source)
        dealt = target.takeDamage(amount, source or self)
        for trait_or_effect in self.traits + self.effects:
            trait_or_effect.afterDamageDealt(self, dealt, target, source)
        return dealt

    def getInfoBar(self) -> str:
        name_str: str = f"{Style.BOLD}{self.name}{Style.RESET}"
        hp_str: str = f"{Style.BRIGHT_RED}{self.hp}/{self.max_hp}hp{Style.RESET}"
        st_str: str = f"{Style.YELLOW}{self.st}/{self.max_st}st{Style.RESET}"
        mn_str: str = f"{Style.BRIGHT_BLUE}{self.mn}/{self.max_mn}mn{Style.RESET}"
        effects_str: str = " ".join([f"[{e.name}]" for e in self.effects])
        if effects_str:
            effects_str = f" {Style.MAGENTA}{effects_str}{Style.RESET}"
        return f"{name_str} | {hp_str} | {st_str} | {mn_str}{effects_str}"

    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        for effect in self.effects[:]:
            effect.onTick(self, skelebash)
            if effect.duration <= 0:
                self.removeEffect(effect)
        for trait in self.traits[:]:
            trait.onTick(self, skelebash)
        for itemstack in self.inventory.itemstacks:
            itemstack.onTick(skelebash)
        for skill in self.skills.skills:
            skill.onTick(skelebash)
        if self.brain:
            self.brain.onTick(self, skelebash)
    def __repr__(self) -> str:
        return f"Entity(\n  '{self.name}',\n  {self.hp}/{self.max_hp}hp,\n  {self.st}/{self.max_st}st,\n  {self.mn}/{self.max_mn}mn,\n  inventory={'\n'.join(['  '+line for line in repr(self.inventory).split('\n') if line.strip()]).strip()}\n)"

class Player(Entity):
    NAME: str = "player"
    DESCRIPTION: str = "you"
    HP: int = 100
    MAX_HP: int = 100
    ST: int = 100
    MAX_ST: int = 100
    MN: int = 0
    MAX_MN: int = 0
    STANCE: Stance = Stance()
    ART: Art = Art()
    ARMAMENT: Armament = Armament()
    SKILL_POINTS: int = 5

    def __init__(self) -> None:
        super().__init__()
        self.stance: Stance = self.STANCE
        self.art: Art = self.ART
        self.armament: Armament = Armament()
        self.skill_points: int = self.SKILL_POINTS