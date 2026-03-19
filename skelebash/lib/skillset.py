from __future__ import annotations
import typing

from .style import Style, printCommandPrompt, printTypewriter
from .skill import Skill
from .keyset import Keyset, KeysetError


class Skillset:
    def __init__(self, *skills: Skill) -> None:
        self.skills: list[Skill] = list(skills)
    def prompt(self, player: Player, target: Entity, keyset: str = Keyset.ZXCVGH) -> Skill: # type: ignore
        if len(self.skills) > 6:
            raise IndexError(f"illegal skillset length. must be 6 or lower, not {len(self.skills)}.")
        if len(keyset) > 6:
            raise KeysetError(f"illegal keyset length. must be 6 or lower, not {len(keyset)}.")
        keymap: dict[str, Skill | typing.Callable] = {}
        for i, (key, skill) in enumerate(zip(keyset, self.skills), start=1):
            if not skill.locked:
                printCommandPrompt(key, f"{i}. {skill.name} (costs {skill.st_cost}ST, {skill.mn_cost}MN)")
                keymap |= {
                    key: skill
                }
            else:
                printCommandPrompt(f"{Style.BRIGHT_BLACK}{Style.STRIKETHROUGH}{key}{Style.RESET}", f"{Style.BRIGHT_BLACK}{Style.STRIKETHROUGH}{i}. {skill.name}{Style.RESET} {Style.BRIGHT_BLACK}(mastery {skill.unlock_at_mastery} required)")
                keymap |= {
                    key: lambda: printTypewriter(f"{Style.RED}skill not unlocked.")
                }
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(repr(skill) for skill in self.skills)})"
class Stance(Skillset):
    ...
class Art(Skillset):
    ...
class Armament(Skillset):
    ...