from __future__ import annotations
import typing


class Goal:
    NAME: str = "unnamed goal"
    DESCRIPTION: str = "no description provided."
    DIFFICULTY: str | None = None
    REWARD_MASTERY: int = 0
    class Difficulty:
        NONE = "\033[38;5;244mnone\033[0m"
        EASY = "\033[32measy (*)\033[0m"
        MEDIUM = "\033[38;5;208mmedium (**)\033[0m"
        HARD = "\033[255;0;0mhard (***)\033[0m"
        RARE = "\033[94mrare (***)\033[0m"
        INSANE = "\033[35minsane (****)\033[0m"
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.difficulty: str = self.DIFFICULTY or Goal.Difficulty.NONE
    def check(self) -> None:
        pass