from __future__ import annotations
import random
import typing

from skelebash.lib.item import Item
from skelebash.lib.itemstack import ItemStack
from skelebash.lib.itembundle import ItemBundle
from skelebash.lib.skill import Skill
from skelebash.lib.entity import Entity, Player
from skelebash.lib.skillset import Skillset
from skelebash.lib.util import newBuffs, newFormula, public, incrpct
from skelebash.lib.goal import Goal
from skelebash.lib.trait import Trait
from skelebash.lib.damagesource import DamageSource
from skelebash.lib.character import Character
from skelebash.lib.style import Style, printTypewriter
from skelebash.lib.animation import SLASH_ANIMATION, PUNCH_ANIMATION

@public
class RatioTechniqueTrait(Trait):
    NAME: str = "7:3 ratio"
    DESCRIPTION: str = "Every attack has a 30% chance to strike the 7:3 ratio point, forcing a critical hit with massively increased damage, ignoring normal crit stats."

    def beforeDamageDealt(self, entity: Entity, amount: int, target: Entity, source: typing.Any = DamageSource.UNKNOWN) -> int:
        if isinstance(source, tuple) and source[0] == DamageSource.SKILL:
            used = source[1]
            if random.randint(1, 100) <= 30:
                printTypewriter(f"{Style.YELLOW}{Style.BOLD}* {entity.name} magically struck the 7:3 ratio point of {target.name}!!! [CRITICAL HIT]{Style.RESET}")
                amount = incrpct(amount, 150)
                used.crit = True # Mark it as a critical hit to downstream systems
        return amount

@public
class OvertimeTrait(Trait):
    NAME: str = "overtime"
    DESCRIPTION: str = "Enters Overtime on Turn 10, massively increasing physical stats."
    
    def __init__(self) -> None:
        super().__init__()
        self.turn_count = 0
        self.active = False
        
    def onTick(self, entity: Entity, skelebash: typing.Any) -> None: # type: ignore
        if not self.active:
            # We increment turn_count, realistically every tick of combat
            self.turn_count += 1
            if self.turn_count >= 10:
                self.active = True
                printTypewriter(f"{Style.BRIGHT_MAGENTA}{Style.BOLD}* {entity.name} checks their watch...{Style.RESET}")
                printTypewriter(f"{Style.BRIGHT_MAGENTA}{Style.BOLD}\"I'm now going into overtime.\"{Style.RESET}")
                entity.strength_pct += 50
                entity.st_recovery += 15
                entity.st += 50 # Immediate stamina burst

@public
class DullBladeStrike(Skill):
    NAME: str = "dull blade strike"
    DESCRIPTION: str = "a fast strike with the wrapped blade. combo extends."
    MESSAGE: str = "{entity} strikes {target} fast with their wrapped blade."
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    CRIT_CHANCE_PCT: int = 15
    CRIT_DAMAGE_PCT: int = 25
    WHIFF_CHANCE_PCT: int = 15
    ST_COST: int = 5
    MN_COST: int = 0
    STARTUP: int = 5
    COOLDOWN: int = 1
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

@public
class RatioSlash(Skill):
    NAME: str = "ratio slash"
    DESCRIPTION: str = "a powerful slashing attack, aiming for the weak point."
    MESSAGE: str = "{entity} slashes violently at {target}."
    BASE_DAMAGE: int = 15
    BASE_STUN: int = 1
    CRIT_CHANCE_PCT: int = 10
    CRIT_DAMAGE_PCT: int = 50
    WHIFF_CHANCE_PCT: int = 20
    ST_COST: int = 8
    MN_COST: int = 0
    STARTUP: int = 8
    COOLDOWN: int = 2
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

@public
class Collapse(Skill):
    NAME: str = "collapse"
    DESCRIPTION: str = "a devastating blow that destroys the environment, leaving the enemy highly vulnerable."
    MESSAGE: str = "{entity} slams their weapon down, causing a massive collapse on {target}!"
    BASE_DAMAGE: int = 25
    BASE_STUN: int = 2
    CRIT_CHANCE_PCT: int = 5
    CRIT_DAMAGE_PCT: int = 100
    WHIFF_CHANCE_PCT: int = 30
    ST_COST: int = 15
    MN_COST: int = 0
    STARTUP: int = 12
    COOLDOWN: int = 4
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

@public
class RatioTechnique(Item):
    NAME: str = "cursed technique: 7:3 ratio"
    DESCRIPTION: str = "a wrapped greatsword embedded with a cursed technique that forces a weak point at the 7:3 ratio."
    RARITY: str | None = Item.Rarity.EPIC
    USABLE: bool = True
    USE_TEXT: str = "equip"
    HAS_LEVELS: bool = True
    HAS_MASTERY: bool = True
    UPGRADE_COSTS: list[ItemBundle] = newFormula(Item, "0")
    UPGRADE_BUFFS: list[list[str]] = newBuffs({
        2: (
            "+{}% damage",
            ("starts", 10),
            ("scaling", "x+10")
        ),
        10: (
            "+{}% crit damage",
            ("starts", 10),
            ("scaling", "x+5")
        )
    })
    GOALS: list[Goal] = []
    
    def __init__(self, enable_mxp_rewards: bool = True) -> None:
        self.SKILLSET = Skillset(DullBladeStrike(), RatioSlash(), Collapse())
        super().__init__(enable_mxp_rewards)

    def onUse(self, entity: Entity) -> None: # type: ignore
        self.equipAsArmament(entity)

    def onSkillUpdate(self, skill: Skill, entity: Entity) -> None: # type: ignore
        skill.extra_damage_pct = skill.EXTRA_DAMAGE_PCT
        skill.crit_damage_pct = skill.CRIT_DAMAGE_PCT
        if self.level >= 2:
            skill.extra_damage_pct += round((self.level - 1) * 10)
        if self.level >= 10:
            skill.crit_damage_pct += round((self.level - 9) * 5)

@public
class RatioSorcerer(Character):
    NAME: str = "ratio sorcerer"
    DESCRIPTION: str = "a former salaryman turned sorcerer who heavily relies on the 7:3 ratio technique."
    STATS: list[str] = [
        "starts with 120/120 hp",
        "starts with 80/80 st",
        "starts with 0/0 mn",
        "starts with 40/40 bh",
        "starts with '7:3 ratio' trait",
        "starts with 'overtime' trait",
        "starts with 'ratio technique' weapon",
        "starts with 'basic' stance"
    ]

    class ENTITY(Player):
        HP: int = 120
        MAX_HP: int = 120
        ST: int = 80
        MAX_ST: int = 80
        MN: int = 0
        MAX_MN: int = 0
        BH: int = 40
        MAX_BH: int = 40
        
        def __init__(self) -> None:
            super().__init__()
            self.armament = Skillset(DullBladeStrike(), RatioSlash(), Collapse())
            self.inventory = ItemBundle(ItemStack(RatioTechnique(), 1))
            self.traits.append(RatioTechniqueTrait())
            self.traits.append(OvertimeTrait())