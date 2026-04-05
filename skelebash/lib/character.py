from __future__ import annotations
import typing
import math

from .entity import Player, Entity
from .item import colorBuff, Greatsword, Stick
from .util import public, incrpct
from .itembundle import ItemBundle
from .itemstack import ItemStack
from .style import printPanel, Style, prompt, printCommandPrompt, breakLine, enterToContinue, clearScreen, printTypewriter, printStyle
from .skillset import Stance, Art, Armament, BalancedStance, NinjaStance, WarriorStance, SorcererStance, MonsterStance, AndroidStance, GlassCannonStance, GlassArt, CopyArt, UnavailableStance, UnavailableArmament
from .trait import Trait, AdaptableTrait, BerserkerTrait, ShadowStepTrait, ManaShieldTrait
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
    def showShortInfo(self) -> None:
        printPanel(f"{Style.BOLD}{self.name}{Style.RESET}\n{self.description}")
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
        "starts with 'adaptable' trait",
        "starts with 'basic' stance"
    ]
    TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
        [("entity", "let's see if you can keep up!"), ("target", "easy for you to say."), ("entity", "heh, just watch.")],
        [("entity", "thought you were fast?"), ("target", "fast enough to beat you."), ("entity", "we'll see about that.")]
    ]
    class ENTITY(Player):
        STANCE: Stance = BalancedStance()
        TAUNT_DIALOGUES = [
            [("entity", "let's see if you can keep up!"), ("target", "easy for you to say."), ("entity", "heh, just watch.")],
            [("entity", "thought you were fast?"), ("target", "fast enough to beat you."), ("entity", "we'll see about that.")]
        ]
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(AdaptableTrait())

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
        STANCE: Stance = WarriorStance()
        ARMAMENT: Armament = Greatsword.SKILLSET
        INVENTORY: ItemBundle = ItemBundle(ItemStack(Greatsword(), 1))
        TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
            [("entity", "c'mon! hit me!"), ("target", "gladly!"), ("entity", "that all you got?")],
            [("entity", "your strength is lacking!"), ("target", "i'll show you strength!"), ("entity", "prove it!")],
            [("entity", "is that all you got?"), ("target", "i'm just getting warmed up!"), ("entity", "we'll see about that.")],
        ]
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(BerserkerTrait())

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
        BLOCK_EFFICIENCY_PCT: int = 75
        AGILITY_PCT: int = 30
        STANCE: Stance = NinjaStance()
        TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
            [("entity", "i didn't expect you to be so slow :P"), ("target", "oh shut up."), ("entity", "heh.")],
            [("entity", "can't catch what you can't see."), ("target", "stop moving so much!"), ("entity", "never.")],
        ]
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(ShadowStepTrait())

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
        "starts with 'manamancer tier i' art",
        "starts with 'stick' armament"
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
        BLOCK_EFFICIENCY_PCT: int = 40
        DURABILITY_PCT: int = 50
        STANCE: Stance = SorcererStance()
        ARMAMENT: Armament = Stick.SKILLSET
        INVENTORY: ItemBundle = ItemBundle(ItemStack(Stick(), 1))
        TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
            [("entity", "focusing on your movements is almost... trivial."), ("target", "wipe that smirk off your face."), ("entity", "only if you can make me.")],
            [("entity", "your aura is flickering. are you tired?"), ("target", "mind your own business!"), ("entity", "oh, i intend to.")],
            [("entity", "think you can beat me with that weak sorcery?"), ("target", "it's stronger than you think!"), ("entity", "we'll see about that.")],
        ]
        def __init__(self) -> None:
            super().__init__()
            self.traits.append(ManaShieldTrait())

@public
class Monster(Character):
    NAME: str = "monster"
    DESCRIPTION: str = "a fast-paced entity that focuses on poison damage over time."
    STATS: list[str] = [
        "starts with 120/120 hp",
        "starts with 150/150 st",
        "starts with 0/0 mn",
        "average startups, focusing on poison for damage over time",
        "starts with 'monster' stance",
    ]
    TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
        [("entity", "SSSSS... you look delicious."), ("target", "stay back, beast!"), ("entity", "HUNGRY...")],
        [("entity", "your blood smells... toxic."), ("target", "gross...")],
    ]
    class ENTITY(Player):
        STANCE: Stance = MonsterStance()
        ST: int = 80
        MAX_ST: int = 80
        def __init__(self) -> None:
            super().__init__()

@public
class Android(Character):
    NAME: str = "android"
    DESCRIPTION: str = "a tanky machine that uses 'charge' instead of stamina."
    STATS: list[str] = [
        "starts with 150/150 hp",
        "starts with 200/200 charge",
        "starts with 0/0 mn",
        "tank with high stats. utilizes 'charge' and 'overcharge'.",
        "rage is replaced with 'overcharge' (infinite charge)",
        "starts with 'android' stance",
    ]
    TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
        [("entity", "SCANNING... THREAT LEVEL: MINIMAL."), ("target", "i'll show you threat!"), ("entity", "DESTRUCTIVE SEQUENCE INITIATED.")],
        [("entity", "YOUR ORGANIC COMPONENTS ARE INEFFICIENT."), ("target", "shut up, bucket of bolts!")],
    ]
    class ENTITY(Player):
        HP: int = 150
        MAX_HP: int = 150
        STRENGTH_PCT: int = 20
        DEFENSE_PCT: int = 20
        ST_LABEL: str = "ch"
        FULL_ST_LABEL: str = "charge"
        STANCE: Stance = AndroidStance()
        def __init__(self) -> None:
            super().__init__()
            from .skill import OverchargeEffect
            # We override the rage effect to be overcharge
            for sk in self.reflex.skills:
                if sk.NAME == "rage":
                    sk.NAME = "overcharge"
                    sk.DESCRIPTION = "infinite charge for 3 turns."
                    def overcharge_afterUse(e, t, u):
                        from .effect import OverchargeEffect
                        OverchargeEffect.apply(e, 1, 3)
                    sk.afterUse = overcharge_afterUse

@public
class GlassCannon(Character):
    NAME: str = "glass cannon"
    DESCRIPTION: str = "a fighter with very low health and defense but massive damage power."
    STATS: list[str] = [
        "starts with 40/40 hp",
        "starts with -20% defense",
        "massive damage output",
        "glass shield blocks 100% of one hit",
        "starts with 'glass resonance' art"
    ]
    TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
        [("entity", "one touch is all i need."), ("target", "and one touch is all it takes to break you."), ("entity", "try to hit me then.")],
        [("entity", "shattering you will be like glass."), ("target", "we'll see who shatters first.")],
    ]
    class ENTITY(Player):
        HP: int = 40
        MAX_HP: int = 40
        MN: int = 50
        MAX_MN: int = 50
        STRENGTH_PCT: int = 50
        DEFENSE_PCT: int = -20
        STANCE: Stance = GlassCannonStance()
        ART: Art = GlassArt()
        def __init__(self) -> None:
            super().__init__()

@public
class ManaVessel(Character):
    NAME: str = "mana vessel"
    DESCRIPTION: str = "a being of pure mana. cannot physically attack but has access to immense mana reserves."
    STATS: list[str] = [
        "starts with 100/100 hp",
        "starts with 0/0 st (cannot be upgraded)",
        "starts with 200/200 mn",
        "cannot use stances or armaments",
        "cannot parry when blocking",
        "starts with 'mana mimicry' art"
    ]
    TAUNT_DIALOGUES: list[list[tuple[str, str]]] = [
        [("entity", "..."), ("target", "what are you?"), ("entity", "...everything.")],
        [("entity", "hollow eyes, infinite depth."), ("target", "stop staring at me!")],
    ]
    class ENTITY(Player):
        ST: int = 0
        MAX_ST: int = 0
        MN: int = 200
        MAX_MN: int = 200
        ART: Art = CopyArt()
        # We must disable stance and armament effectively
        STANCE: Stance = UnavailableStance()
        ARMAMENT: Armament = UnavailableArmament()
        def __init__(self) -> None:
            super().__init__()
            # Disable parries and blocks
            from .skillset import Reflex
            from .skill import Burst, Rage, Taunt
            self.reflex = Reflex(Burst(), Rage(), Taunt())
            # Ensure max_st stays 0
            self.st = 0
            self.max_st = 0

BASE_CHARACTER_LIST: list[Character] = [Balanced(), Warrior(), Ninja(), Sorcerer(), Monster(), Android(), GlassCannon(), ManaVessel()]

def chooseCharacter(chars: list[Character], choose: str | None = None) -> Character | None:
    first: bool = True
    while True:
        clearScreen()
        for char in chars:
            char.showShortInfo()
        for i, char in enumerate(chars, 1):
            printCommandPrompt(str(i), char.name, (printStyle if choose or not first else printTypewriter))
        printCommandPrompt("c", "cancel", (printStyle if choose or not first else printTypewriter))
        breakLine()
        first = False
        choice: str = choose or prompt("character select", safe=True)
        if not choice:
            continue
        elif choice == "c":
            return
        elif choice.isdigit():
            choice_idx: int = int(choice) - 1
            if 0 <= choice_idx < len(chars):
                while True:
                    clearScreen()
                    char: Character = chars[choice_idx]
                    char.showInfo()
                    printCommandPrompt("c", "confirm", (printStyle if choose or not first else printTypewriter))
                    printCommandPrompt("b", "back", (printStyle if choose or not first else printTypewriter))
                    choice2: str = "c" if choose else prompt("character select", safe=True)
                    if not choice2:
                        continue
                    elif choice2 == "c":
                        return char
                    elif choice2 == "b":
                        break
                    else:
                        printTypewriter(f"{Style.RED}invalid input.")
                        enterToContinue()
        else:
            printTypewriter(f"{Style.RED}invalid input.")
            enterToContinue()