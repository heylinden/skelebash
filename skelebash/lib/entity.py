from __future__ import annotations
import typing

from .item import Item
from .itembundle import ItemBundle
from .style import Style
from .skill import Skill
from .skillset import Armament, Art, Skillset, Stance, FollowUp, Reflex
from .effect import Effect
from .trait import Trait
from .damagesource import DamageSource
from .brain import Brain
from .util import pct


class Entity:
    NAME: str = "unknown"
    DESCRIPTION: str = "no description"
    HP: int = 100 # hit points
    MAX_HP: int = 100
    HP_RECOVERY: int = 0 # hit points regenerated per turn
    ST: int = 100 # stamina
    MAX_ST: int = 100
    ST_RECOVERY: int = 10 # stamina regenerated per turn
    MN: int = 0 # mana
    MAX_MN: int = 0
    MN_RECOVERY: int = 10 # mana regenerated per turn
    BH: int = 20 # block health
    MAX_BH: int = 20
    BH_RECOVERY: int = 5 # block health regenerated per turn
    STRENGTH_PCT: int = 0 # % outgoing damage increase
    DEFENSE_PCT: int = 0 # % incoming damage reduction
    PRECISION_PCT: int = 0 # % outgoing crit chance increase
    FORCE_PCT: int = 50 # % outgoing crit damage increase
    CONCENTRATION_PCT: int = 0 # % outgoing whiff chance reduction
    AGILITY_PCT: int = 0 # % incoming whiff chance increase
    DURABILITY_PCT: int = 0 # % incoming crit chance reduction
    
    BLOCK_STRENGTH_PCT: int = 0 # % outgoing damage to block increase
    BLOCK_EFFICIENCY_PCT: int = 50 # % incoming damage to block reduction

    HYPERARMOR_STRENGTH_PCT: int = 50 # % outgoing damage to hyperarmor increase
    HYPERARMOR_DEFENSE_PCT: int = 0 # % incoming damage to hyperarmor reduction
    
    HP_LABEL: str = "hp"
    FULL_HP_LABEL: str = "hit points"
    ST_LABEL: str = "st"
    FULL_ST_LABEL: str = "stamina"
    MN_LABEL: str = "mn"
    FULL_MN_LABEL: str = "mana"
    BH_LABEL: str = "bh"
    FULL_BH_LABEL: str = "block health"
    SUPER_LABEL: str = "%"
    FULL_SUPER_LABEL: str = "super"
    
    STUN: int = 0
    IFRAMES: bool = False

    INVENTORY: ItemBundle = ItemBundle()
    SKILLS: Skillset = Skillset()

    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.hp: int = self.HP
        self.max_hp: int = self.MAX_HP
        self.hp_recovery: int = self.HP_RECOVERY
        self.st: int = self.ST
        self.max_st: int = self.MAX_ST
        self.st_recovery: int = self.ST_RECOVERY
        self.mn: int = self.MN
        self.max_mn: int = self.MAX_MN
        self.mn_recovery: int = self.MN_RECOVERY
        self.bh: int = self.BH
        self.max_bh: int = self.MAX_BH
        self.bh_recovery: int = self.BH_RECOVERY
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
        self.hyperarmor: int = 0
        self.stun: int = self.STUN
        self.iframes: bool = self.IFRAMES
        self.inventory: ItemBundle = self.INVENTORY
        self.used: list[Skill.Used] = []
        self.skills: Skillset = self.SKILLS
        self.last_skill_used: Skill.Used | None = None
        self.effects: list[Effect] = []
        self.traits: list[Trait] = []
        self.brain: Brain | None = None
    
    def calculate(self, attribute: str) -> int:
        value: int = getattr(self, attribute)
        for trait_or_effect in self.traits + self.effects:
            value = trait_or_effect.returnAttribute(attribute, value)
        return value
    def heal(self, amount: int = None) -> "Entity":
        max_hp = self.calculate("max_hp")
        amount = amount or max_hp - self.hp
        self.hp += min(amount, max_hp - self.hp)
        return self
    def healStamina(self, amount: int = None) -> "Entity":
        max_st = self.calculate("max_st")
        amount = amount or max_st - self.st
        self.st += min(amount, max_st - self.st)
        return self
    def healMana(self, amount: int = None) -> "Entity":
        max_mn = self.calculate("max_mn")
        amount = amount or max_mn - self.mn
        self.mn += min(amount, max_mn - self.mn)
        return self

    def addEffect(self, effect: Effect) -> None:
        self.effects.append(effect)
        effect.onApply(self)

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
        if self.iframes:
            printTypewriter(f"{Style.MAGENTA}* {self.name} is protected by i-frames!{Style.RESET}")
            return 0
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

    def getInfoBar(self, fighting: bool = False) -> str:
        name_str: str = f"{Style.BOLD}{self.name}{Style.RESET}"
        hp_str: str = f"{Style.BRIGHT_RED}{self.hp}/{self.calculate('max_hp')}{self.HP_LABEL}{Style.RESET}"
        st_str: str = f"{Style.YELLOW}{self.st}/{self.calculate('max_st')}{self.ST_LABEL}{Style.RESET}"
        mn_str: str = f"{Style.BRIGHT_BLUE}{self.mn}/{self.calculate('max_mn')}{self.MN_LABEL}{Style.RESET}"
        
        super_str: str = ""
        if isinstance(self, Player):
            super_str = f" | {Style.REDDISH_PINK}{Style.BOLD}{self.FULL_SUPER_LABEL}: {self.super}{self.SUPER_LABEL}{Style.RESET}"

        effects_str: str = " ".join([f"[{e.name}]" for e in self.effects])
        if effects_str:
            effects_str = f" {Style.MAGENTA}{effects_str}{Style.RESET}"
        return f"{Style.BRIGHT_GREEN}{Style.BOLD}{'[FIGHTING] ' if fighting else ''}{Style.RESET}{name_str} | {hp_str} | {st_str} | {mn_str}{super_str}{effects_str}"
    
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        hp_recovery = self.calculate("hp_recovery")
        if hp_recovery:
            self.heal(hp_recovery)
        st_recovery = self.calculate("st_recovery")
        if st_recovery:
            self.healStamina(st_recovery)
        mn_recovery = self.calculate("mn_recovery")
        if mn_recovery:
            self.healMana(mn_recovery)
        bh_recovery = self.calculate("bh_recovery")
        if bh_recovery:
            self.bh = min(self.calculate("max_bh"), self.bh + bh_recovery)
        if self.stun >= 1:
            self.stun -= 1
        for effect in self.effects[:]:
            effect.onTick(self, skelebash)
            if effect.duration <= 0:
                self.removeEffect(effect)
        for trait in self.traits[:]:
            trait.onTick(self, skelebash)
        for itemstack in self.inventory.itemstacks:
            itemstack.onTick(skelebash)
        self.skills.onTick(self, skelebash)
        if self.brain:
            self.brain.onTick(self, skelebash)
    def __repr__(self) -> str:
        inventory_items: str = '\n'.join(['  '+line for line in repr(self.inventory).split('\n') if line.strip()]).strip()
        return f"Entity(\n  '{self.name}',\n  {self.hp}/{self.calculate('max_hp')}hp,\n  {self.st}/{self.calculate('max_st')}st,\n  {self.mn}/{self.calculate('max_mn')}mn,\n  inventory={inventory_items}\n)"

class Player(Entity):
    NAME: str = "player"
    DESCRIPTION: str = "you"
    HP: int = 100
    MAX_HP: int = 100
    ST: int = 100
    MAX_ST: int = 100
    MN: int = 0
    MAX_MN: int = 0
    SUPER: int = 0
    MAX_SUPER: int = 100
    SUPER_GAIN_PCT: int = 100
    BURST_COST: int = 30
    BURST_COOLDOWN: int = 4
    BURST_STARTING_COOLDOWN: int = 0
    
    STANCE: Stance = Stance()
    ART: Art = Art()
    ARMAMENT: Armament = Armament()
    FOLLOW_UP: FollowUp = FollowUp()
    SKILL_POINTS: int = 5

    def __init__(self) -> None:
        super().__init__()
        self.super: int = self.SUPER
        self.max_super: int = self.MAX_SUPER
        self.super_gain_pct: int = self.SUPER_GAIN_PCT
        self.burst_cost: int = self.BURST_COST
        self.burst_base_cooldown: int = self.BURST_COOLDOWN
        self.burst_active_cooldown: int = self.BURST_STARTING_COOLDOWN
        self.stance: Stance = self.STANCE
        self.art: Art = self.ART
        self.armament: Armament = self.ARMAMENT
        from .skill import QuickBlock, SlowBlock, Deflect, Burst, Rage, Taunt
        self.reflex: Reflex = Reflex(QuickBlock(), SlowBlock(), Deflect(), Burst(), Rage(), Taunt())
        self.follow_up: FollowUp = self.FOLLOW_UP
        self.skill_points: int = self.SKILL_POINTS
    def dealDamage(self, amount: int, target: Entity, source: DamageSource | tuple[DamageSource, typing.Any] = DamageSource.UNKNOWN) -> int:
        dealt = super().dealDamage(amount, target, source)
        self.super = min(self.max_super, pct(self.super + dealt, self.calculate("super_gain_pct")))
        return dealt
    def takeDamage(self, amount: int, source: typing.Any) -> int:
        taken = super().takeDamage(amount, source)
        self.super = min(self.max_super, pct(self.super + taken, self.calculate("super_gain_pct")))
        return taken
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        super().onTick(skelebash)
        if skelebash.room.enemies[0]:
            self.used.clear()
        self.stance.onTick(self, skelebash)
        self.art.onTick(self, skelebash)
        self.armament.onTick(self, skelebash)
        self.follow_up.onTick(self, skelebash)