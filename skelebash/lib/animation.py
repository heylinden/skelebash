from __future__ import annotations
import time, pathlib, typing

from .style import clearScreen, printStyle, Style
from .constants import ANIMATIONS_DIR, ANIMATION_BUFFER


class Animation:
    def __init__(self, *frames: str, name: str = "animation", delay: float = 0.1) -> None:
        self.frames: list[str] = list(frames)
        self.name: str = name
        self.delay: float = delay
    def __matmul__(self, delay: int) -> "Animation":
        animation: Animation = self.__class__(*self.frames, name=self.name, delay=delay)
        return animation
    @classmethod
    def get(cls, name: str, delay: float = 0.1, **kwargs: typing.Any) -> "Animation":
        frames: list[str] = []
        for path in sorted((ANIMATIONS_DIR / name).iterdir(), key=lambda p: p.name):
            with path.open() as file:
                frames.append(eval(f"f\"\"\"{file.read()}\"\"\"", {"Style": Style, **kwargs}) + Style.RESET)
        return cls(*frames, name=name, delay=delay)
    def play(self, loop: int = 1) -> None:
        for frame in self.frames * loop:
            printStyle(f"{'\n'*ANIMATION_BUFFER}{' '*ANIMATION_BUFFER+frame.replace('\n', '\n' + ' '*ANIMATION_BUFFER)}")
            time.sleep(self.delay)
            clearScreen()

LEVEL_UP_ANIMATION: Animation = Animation.get("level_up", 0.05)
MASTERY_UP_ANIMATION: Animation = Animation.get("mastery_up", 0.05)
CLASH_ANIMATION: Animation = Animation.get("clash", 0.05)
EXPLOSION_ANIMATION: Animation = Animation.get("explosion", 0.05)
FIRE_ANIMATION: Animation = Animation.get("fire", 0.05)
ICE_ANIMATION: Animation = Animation.get("ice", 0.05)
KICK_ANIMATION: Animation = Animation.get("kick", 0.05)
PUNCH_ANIMATION: Animation = Animation.get("punch", 0.05)
SLASH_ANIMATION: Animation = Animation.get("slash", 0.05)
STRIKE_ANIMATION: Animation = Animation.get("strike", 0.05)
WIND_ANIMATION: Animation = Animation.get("wind", 0.05)