from __future__ import annotations
import math, re

from .skillset import Skillset
from .skill import Skill
from .itembundle import ItemBundle, countItems
from .itemstack import ItemStack
from .style import breakLine, clearScreen, enterToContinue, printCommandPrompt, printPanel, printCentered, printStyle, Style, printTypewriter, prompt
from .animation import LEVEL_UP_ANIMATION, MASTERY_UP_ANIMATION
from .goal import Goal
from .util import public


def colorBuff(buff: str) -> str:
    keywords: dict[str, str] = {
        "poison damage": Style.BRIGHT_GREEN,
        "poison": Style.BRIGHT_GREEN,
        "venom damage": Style.BRIGHT_ORANGE,
        "venom": Style.BRIGHT_ORANGE,
        "recoil damage": Style.BRIGHT_BLACK,
        "recoil": Style.BRIGHT_BLACK,
        "decay damage": Style.BLACK,
        "decay": Style.BLACK,
        "bleeding damage": Style.BRIGHT_RED + Style.BOLD,
        "bleeding": Style.BRIGHT_RED + Style.BOLD,
        "lifesteal damage": Style.RED + Style.BOLD,
        "lifesteal": Style.RED + Style.BOLD,
        "damage": Style.RED,
        "crit chance": Style.YELLOW + Style.BOLD,
        "health": Style.BRIGHT_RED,
        "stamina": Style.YELLOW,
        "mana": Style.BRIGHT_BLUE,
        "mastery": Style.BLUE + Style.BOLD,
        "level": Style.YELLOW + Style.BOLD,
        "rarity": Style.BOLD,
        "i-frames": Style.MAGENTA + Style.BOLD,
        "stun": Style.ORANGE + Style.BOLD
    }
    
    def replace_color(match: re.Match):
        keyword: str = match.group(0)
        color: str = keywords.get(keyword, "")
        return f"{color}{keyword}{Style.RESET}"
    
    pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
    return re.sub(pattern, replace_color, buff)

class Item:
    NAME: str = "unknown"
    DESCRIPTION: str = "no description"
    RARITY: str | None = None
    USABLE: bool = False 
    USE_TEXT: str = "use"
    HAS_LEVELS: bool = False
    HAS_MASTERY: bool = False
    UPGRADE_COSTS: list[ItemBundle] = []
    UPGRADE_BUFFS: list[list[str]] = []
    GOALS: list[Goal] = []
    SKILLSET: Skillset | None = None
    class Rarity:
        NONE = "\033[38;5;244mnone\033[0m"
        COMMON = "\033[38;5;244mcommon (*)\033[0m"
        UNCOMMON = "\033[32muncommon (**)\033[0m"
        RARE = "\033[94mrare (***)\033[0m"
        EPIC = "\033[35mepic (****)\033[0m"
        LEGENDARY = "\033[38;5;208mlegendary (*****)\033[0m"
        MYTHIC = "\033[38;5;220mmythic (******)\033[0m"
        DIVINE = "\033[1;38;5;117mdivine (*******)\033[0m"
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.rarity: str = self.RARITY or Item.Rarity.NONE
        self.usable: bool = self.USABLE
        self.use_text: str = self.USE_TEXT.strip()
        self.level: int = int(self.HAS_LEVELS)
        self.mastery: int = int(self.HAS_MASTERY) - 1
        self.upgrade_costs: list[ItemBundle] = self.UPGRADE_COSTS
        self.upgrade_buffs: list[list[str]] = self.UPGRADE_BUFFS
        self.goals: list[Goal] = self.GOALS
        self.skillset: Skillset | None = self.SKILLSET
    def calculateUpgradeCosts(self) -> list[ItemBundle]:
        upgrade_costs: list[ItemBundle] = []
        if not self.upgrade_costs:
            return upgrade_costs

        n: int = len(self.upgrade_costs)
        last: ItemBundle = self.upgrade_costs[-1]

        for level in range(1, 31):
            idx: int = (level - 1) % n
            wraps: int = (level - 1) // n

            within: ItemBundle = self.upgrade_costs[idx]
            extra: list[ItemStack] = [ItemStack(s.item, s.count * wraps) for s in last.itemstacks]

            total: ItemBundle = ItemBundle(*countItems(*within.itemstacks, *extra))
            upgrade_costs.append(total)

        return upgrade_costs
    def __mul__(self, n: int) -> ItemStack:
        return ItemStack(self, n)
    def __pow__(self, n: int) -> ItemStack:
        return public(ItemStack(self, n))
    def __eq__(self, other: Item) -> bool:
        return self.NAME == other.NAME
    def showInfo(self, entity: Entity, skelebash: Skelebash, allow_use: bool = True, allow_upgrade: bool = True, allow_goals_view: bool = True) -> None: # type: ignore
        first: bool = True
        while True:
            clearScreen()
            printPanel(f"{self.name} [{self.rarity}]")
            use_command: str = "e" if self.use_text.strip()[0] in "bu" else self.use_text.strip()[0]
            if self.level:
                printPanel(f"{Style.YELLOW}{Style.BOLD}level {self.level}/{30}{Style.RESET}{''.join(['\n'+colorBuff(buff) for buff in self.upgrade_buffs[self.level - 1]])}")
            if self.mastery != -1:
                printPanel(f"{Style.BRIGHT_BLUE}{Style.BOLD}mastery {math.floor(self.mastery / 100)}{Style.RESET}{Style.BRIGHT_BLUE}\n[{'█' * ((self.mastery % 100) // 10) + '░' * (10 - (self.mastery % 100) // 10)}] {self.mastery % 100}/100mXP until {self.mastery // 100 + 1}")
            ((lambda text: printTypewriter(text, 0.01) )if first else printStyle)(f"{Style.BOLD}description: {Style.RESET}{self.description}")
            if self.skillset and self.skillset.skills:
                breakLine()
                for skill in self.skillset.skills:
                    skill.showInfo(first)
                breakLine()
            if self.usable and allow_use:
                printCommandPrompt(use_command, self.use_text, ((lambda text: printTypewriter(text, 0.005)) if first else printStyle))
            if self.level and allow_upgrade:
                can_upgrade: bool = entity.inventory.has(*self.calculateUpgradeCosts()[self.level - 1])
                max_level: bool = self.level >= 30
                printCommandPrompt("u", f"{Style.BRIGHT_GREEN if can_upgrade and not max_level else Style.RED}upgrade this item ({', '.join([(str(itemstack.count)+'x '+itemstack.item.name) for itemstack in self.upgrade_costs[self.level - 1]])}){' | NOT ENOUGH RESOURCES' if not can_upgrade else (' | MAX LEVEL' if max_level else '')}", ((lambda text: printTypewriter(text, 0.005)) if first else printStyle))
            printCommandPrompt("b", "back", ((lambda text: printTypewriter(text, 0.005)) if first else printStyle))
            printCommandPrompt("?", "help", ((lambda text: printTypewriter(text, 0.005)) if first else printStyle))
            inp: str = prompt("item", skelebash)
            if inp == use_command and self.usable and allow_use:
                self.onUse(entity)
            elif inp == "u" and self.level and allow_upgrade:
                if self.level >= 30:
                    printTypewriter(f"{Style.YELLOW}{self.name} is already at max level! (30)")
                    enterToContinue()
                else:
                    itembundle: ItemBundle = self.calculateUpgradeCosts()[self.level - 1]
                    if not entity.inventory.has(*itembundle.itemstacks):
                        printTypewriter(f"{Style.RED}you don't have enough items to upgrade!")
                        enterToContinue()
                    else:
                        self.onUpgrade(entity)
                        for itemstack in itembundle:
                            entity.inventory.remove(itemstack)
                        self.level += 1
            elif inp == "g" and self.goals and allow_goals_view:
                for goal in self.goals:
                    goal.showInfo()
                enterToContinue()
            elif inp == "?":
                printTypewriter(
                    f"each item has one of seven possible {Style.BOLD}rarities{Style.RESET}.\n"
                    f"* list of rarities in order from lowest to highest:\n"
                    f"  1. {Item.Rarity.COMMON},\n"
                    f"  2. {Item.Rarity.UNCOMMON},\n"
                    f"  3. {Item.Rarity.RARE},\n"
                    f"  4. {Item.Rarity.EPIC},\n"
                    f"  5. {Item.Rarity.LEGENDARY},\n"
                    f"  6. {Item.Rarity.MYTHIC},\n"
                    f"  7. {Item.Rarity.DIVINE}.\n"
                    f"some items have a {Style.YELLOW}{Style.BOLD}level{Style.RESET}.\n"
                    f"* each level increases the effectiveness of the item (damage, healing, etc.)\n"
                    f"  and gives a small boost to mastery gain. {Style.BRIGHT_BLACK}1 + ((level - 1) / 29) * 0.2{Style.RESET}\n"
                    f"* you can upgrade a supported item using a set item/resource requirement\n"
                    f"  that scales every upgrade.\n"
                    f"* levels are always capped at 30.\n"
                    f"weapons have a {Style.BRIGHT_BLUE}{Style.BOLD}mastery{Style.RESET} level too.\n"
                    f"* mastery unlocks more skills as you progress.\n"
                    f"* gain mastery xp (mXP) by landing skills, crits or\n"
                    f"  completing item goals.\n"
                    f"* 1 mastery level = 100mXP. mastery level is uncapped.",
                    delay=0.005
                )
                enterToContinue()
            elif inp == "b":
                return
            first = False
    def addMastery(self, mxp: int, entity: Entity) -> None: # type: ignore
        multiplier: float = 1.0
        mastery_before: int = self.mastery
        if self.level > 1:
            multiplier = 1 + ((self.level - 1) / 29) * 0.2
        self.mastery += round(mxp * multiplier)
        if math.floor(self.mastery / 100) > math.floor(mastery_before / 100):
            self.onMasteryUpgrade(entity)
    def masteryUp(self, entity: Entity) -> None: # type: ignore
        self.addMastery(100, entity)
    def levelUp(self, n: int, entity: Entity) -> None: # type: ignore
        self.level += n
        self.onUpgrade(entity)
    def equipAsArmament(self, entity: Entity) -> None: # type: ignore
        entity.armament = self.skillset
        printTypewriter(f"equipped {self.name} as armament.")
        enterToContinue()
    def onUse(self, entity: Entity) -> None: # type: ignore
        enterToContinue()
    def onUpgrade(self, entity: Entity) -> None: # type: ignore
        LEVEL_UP_ANIMATION.play(1)
    def onMasteryUpgrade(self, entity: Entity) -> None: # type: ignore
        MASTERY_UP_ANIMATION.play(1)
    def onTick(self, skelebash: Skelebash) -> None: # type: ignore
        for goal in self.goals:
            goal.onTick(skelebash)
    def __repr__(self) -> str:
        return f"Item('{self.name}')"