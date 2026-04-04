from __future__ import annotations
import typing

from .util import public


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
        self.completed: bool = False
    def onTick(self, skelebash: Skelebash, item: Item) -> None:
        self.completed = bool(self.check(skelebash, item))
    def check(self, skelebash: Skelebash, item: Item) -> bool:
        return False
    def __repr__(self) -> str:
        return f"Goal('{self.name}')"

@public
class MaxLevelGoal(Goal):
    NAME: str = "max level"
    DESCRIPTION: str = "reach max level (30) on this item."
    DIFFICULTY: str = Goal.Difficulty.HARD
    REWARD_MASTERY: int = 500
    def check(self, skelebash: Skelebash, item: Item) -> bool:
        return item.level == 30