from __future__ import annotations
import typing
import math

from .entity import Player, Entity
from .item import colorBuff, Greatsword, Stick
from .util import public, incrpct
from .itembundle import ItemBundle
from .itemstack import ItemStack
from .style import printPanel, Style, prompt, printCommandPrompt, breakLine, enterToContinue, clearScreen, printTypewriter
from .skillset import Stance, Armament
from .trait import Trait
from .damagesource import DamageSource


class Character:
    NAME: str = "unnamed character"
    DESCRIPTION: str = "no description provided."
    STATS: list[str] = []
    ENTITY: type[Player] = Player
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.stats: list[str] = self.STATS
        self.entity: type[Player] = self.ENTITY
    def showInfo(self) -> None:
        printPanel(f"{Style.BOLD}{self.name}{Style.RESET}\n{self.description}\n----\n{colorBuff('\n'.join(self.stats))}")
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(\n  '{self.name}',\n  entity={'\n'.join(['  '+line for line in repr(self.entity).split('\n') if line.strip()]).strip()})"

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
class Balanced(Character):
    NAME: str = "balanced"
    DESCRIPTION: str = "a balanced character with average stats."
    STATS: list[str] = [
        "starts with 100/100 hp",
        "starts with 100/100 st",
        "starts with 0/0 mn",
        "starts with 30/30 bh",
        "starts with 'adaptable' trait",
        "starts with 'basic' stance"
    ]
    class ENTITY(Player):
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(AdaptableTrait())

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
class Warrior(Character):
    NAME: str = "warrior"
    DESCRIPTION: str = "a warrior with heavy-hitting but limited attacks."
    STATS: list[str] = [
        "starts with 120/120 hp",
        "starts with 60/60 st",
        "starts with 0/0 mn",
        "starts with 50/50 bh",
        "starts with 1.3x damage",
        "starts with 1.3x force",
        "starts with 0.7x agility",
        "starts with 'bloodlust' trait",
        "starts with 'warrior' stance",
        "starts with 'greatsword' armament and item"
    ]
    class ENTITY(Player):
        HP: int = 120
        MAX_HP: int = 120
        ST: int = 60
        MAX_ST: int = 60
        MN: int = 0
        MAX_MN: int = 0
        BH: int = 50
        MAX_BH: int = 50
        STRENGTH_PCT: int = 30
        FORCE_PCT: int = 30
        AGILITY_PCT: int = -30
        ARMAMENT: Armament = Greatsword.SKILLSET
        INVENTORY: ItemBundle = ItemBundle(ItemStack(Greatsword(), 1))
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(BerserkerTrait())

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
class Ninja(Character):
    NAME: str = "ninja"
    DESCRIPTION: str = "a ninja with lower health but fast attacks and high mobility."
    STATS: list[str] = [
        "starts with 60/60 hp",
        "starts with 120/120 st",
        "starts with 0/0 mn",
        "starts with 20/20 bh",
        "starts with 0.7x damage",
        "starts with 1.5x block efficiency",
        "starts with 1.3x agility",
        "starts with 'shadow step' trait",
        "starts with 'ninja' stance"
    ]
    class ENTITY(Player):
        HP: int = 60
        MAX_HP: int = 60
        ST: int = 120
        MAX_ST: int = 120
        BH: int = 20
        MAX_BH: int = 20
        STRENGTH_PCT: int = -30
        BLOCK_EFFICIENCY_PCT: int = 90
        AGILITY_PCT: int = 30
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(ShadowStepTrait())

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

@public
class Sorcerer(Character):
    NAME: str = "sorcerer"
    DESCRIPTION: str = "a sorcerer with high magic power but low physical defense."
    STATS: list[str] = [
        "starts with 80/80 hp",
        "starts with 20/20 st",
        "starts with 100/100 mn",
        "starts with 20/20 bh",
        "starts with 1.5x block efficiency",
        "starts with 1.5x durability",
        "starts with 'mana shield' trait",
        "starts with 'sorcerer' stance",
        "starts with 'stick' armament (6 focus skills)",
        "starts with 'reflex' skillset (5 moves)",
        "super meter enabled"
    ]
    class ENTITY(Player):
        HP: int = 80
        MAX_HP: int = 80
        ST: int = 20
        MAX_ST: int = 20
        MN: int = 100
        MAX_MN: int = 100
        BH: int = 20
        MAX_BH: int = 20
        BLOCK_EFFICIENCY_PCT: int = 90
        DURABILITY_PCT: int = 50
        ARMAMENT: Armament = Stick.SKILLSET
        INVENTORY: ItemBundle = ItemBundle(ItemStack(Stick(), 1))
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(ManaShieldTrait())


BASE_CHARACTER_LIST: list[Character] = [Balanced(), Warrior(), Ninja(), Sorcerer()]

def chooseCharacter(chars: list[Character], choose: str | None = None) -> Character | None:
    clearScreen()
    for char in chars:
        char.showInfo()
    for i, char in enumerate(chars, 1):
        printCommandPrompt(str(i), char.name)
    printCommandPrompt("c", "cancel")
    breakLine()
    while True:
        choice: str = choose or prompt("character select", safe=True)
        if not choice:
            continue
        elif choice == "c":
            return
        elif choice.isdigit():
            choice_idx: int = int(choice) - 1
            if 0 <= choice_idx < len(chars):
                return chars[choice_idx]
        else:
            printTypewriter(f"{Style.RED}invalid input.")
            enterToContinue()