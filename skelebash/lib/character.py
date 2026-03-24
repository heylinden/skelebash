from __future__ import annotations

from .entity import Player
from .item import colorBuff, Greatsword
from .util import public
from .itembundle import ItemBundle
from .itemstack import ItemStack
from .style import printPanel, Style, prompt, printCommandPrompt, breakLine, enterToContinue, clearScreen, printTypewriter
from .skillset import Stance, Armament


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
class Balanced(Character):
    NAME: str = "balanced"
    DESCRIPTION: str = "a balanced character with average stats."
    STATS: list[str] = [
        "starts with 100/100 hp",
        "starts with 100/100 st",
        "starts with 0/0 mn",
        "starts with 30/30 bh",
        "starts with 'basic' stance"
    ]
    ENTITY: type[Player] = Player
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
        "starts with 'ninja' stance"
    ]
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
        "starts with 'sorcerer' stance",
        "starts with 'stick' armament and item"
    ]
    

BASE_CHARACTER_LIST: list[Character] = [Balanced(), Warrior(), Ninja(), Sorcerer()]

def chooseCharacter(chars: list[Character], choose: str | None = None) -> Character | None:
    clearScreen()
    for i, char in enumerate(chars, 1):
        char.showInfo()
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