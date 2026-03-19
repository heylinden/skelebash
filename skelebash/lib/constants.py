from __future__ import annotations
import typing, pathlib

from .style import Style


ADJECTIVES: list[str] = [
    "big",
    "small",
    "tiny",
    "huge",
    "red",
    "green",
    "blue",
    "yellow",
    "brown",
    "purple",
    "orange",
    "dark",
    "light",
    "cool",
    "awesome",
    "excited",
    "angry",
    "happy",
    "sad",
    "smart",
    "annoyed",
    "giant",
    "normal",
    "cyan",
    "swift",
    "friendly",
    "scary"
]
NOUNS: list[str] = [
    "skeleton",
    "zombie",
    "rabbit",
    "goat",
    "cat",
    "dog",
    "vulture",
    "bird",
    "elephant",
    "giraffe",
    "crow",
    "capybara",
    "fly",
    "shark",
    "fish",
    "tuna",
    "horse",
    "corn",
    "spider",
    "scorpion",
    "goblin",
    "demon",
    "angel",
    "monster"
]
ENEMY_PARAM: str = f"{Style.RED}{Style.BOLD}e{Style.RESET}"
SKILL_PARAM: str = f"{Style.BLUE}{Style.BOLD}s{Style.RESET}"
ITEM_PARAM: str = f"{Style.YELLOW}{Style.BOLD}i{Style.RESET}"
SAVES_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent / "saves"
CORE_DIR: pathlib.Path = pathlib.Path(__file__).parent
MODS_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent / "mods"
ANIMATIONS_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent / "animations"
PUBLIC_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent / "public"
LAST_OPENED_FILE: pathlib.Path = pathlib.Path(__file__).parent.parent / "LAST_OPENED.txt"