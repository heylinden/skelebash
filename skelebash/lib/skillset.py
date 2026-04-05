from __future__ import annotations
import typing

from .style import Style, printCommandPrompt, printTypewriter
from .skill import (
    Skill, SkillType, Punch, Kick, Hook, Uppercut, RoundhouseKick, Tackle,
    QuickStrike, DoubleTap, TripleStrike, BackflipKick, ShadowStrike, DaggerThrow,
    HeavyStrike, CrushingBlow, ShoulderBash, OverheadSwing, GreatSwing, Brace,
    ManaBolt, ArcaneSlap, MagicMissile, ManaBurst, ArcanePoke, ElementalStrike
)
from .keyset import Keyset, KeysetError


class Skillset:
    NAME: str | None = None
    def __init__(self, *skills: Skill) -> None:
        self.name: str = self.NAME
        self.skills: list[Skill] = list(skills)
    def get(self, index: int) -> Skill:
        return self.skills[index]
    def __getitem__(self, index: int) -> Skill:
        return self.get(index)
    def prompt(self, player: Player, target: Entity, keyset: str = Keyset.ZXCVGH) -> Skill: # type: ignore
        if len(self.skills) > 6:
            raise IndexError(f"illegal skillset length. must be 6 or lower, not {len(self.skills)}.")
        if len(keyset) > 6:
            raise KeysetError(f"illegal keyset length. must be 6 or lower, not {len(keyset)}.")
        keymap: dict[str, Skill | typing.Callable] = {}
        for i, (key, skill) in enumerate(zip(keyset, self.skills), start=1):
            if not skill.locked:
                printCommandPrompt(key, f"{i}. {skill.name} (costs {skill.st_cost}{player.ST_LABEL.upper()}, {skill.mn_cost}{player.MN_LABEL.upper()})")
                keymap |= {
                    key: skill
                }
            else:
                printCommandPrompt(f"{Style.BRIGHT_BLACK}{Style.STRIKETHROUGH}{key}{Style.RESET}", f"{Style.BRIGHT_BLACK}{Style.STRIKETHROUGH}{i}. {skill.name}{Style.RESET} {Style.BRIGHT_BLACK}(mastery {skill.unlock_at_mastery} required)")
                keymap |= {
                    key: lambda: printTypewriter(f"{Style.RED}skill not unlocked.")
                }
    
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        for skill in self.skills:
            skill.onTick(entity, skelebash)
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(repr(skill) for skill in self.skills)})"
class Stance(Skillset):
    pass
class Art(Skillset):
    pass
class Armament(Skillset):
    pass
class Reflex(Skillset):
    pass
class FollowUp(Skillset):
    pass
class BalancedStance(Stance):
    NAME = "balanced"
    def __init__(self) -> None:
        super().__init__(Punch(), Kick(), Hook(), Uppercut(), RoundhouseKick(), Tackle())

class NinjaStance(Stance):
    NAME = "ninja"
    def __init__(self) -> None:
        super().__init__(QuickStrike(), DoubleTap(), TripleStrike(), BackflipKick(), ShadowStrike(), DaggerThrow())

class WarriorStance(Stance):
    NAME = "warrior"
    def __init__(self) -> None:
        super().__init__(HeavyStrike(), CrushingBlow(), ShoulderBash(), OverheadSwing(), GreatSwing(), Brace())

class SorcererStance(Stance):
    NAME: str = "sorcerer"
    def __init__(self) -> None:
        from .skill import ManaBolt, ArcaneSlap, MagicMissile, ManaBurst, ArcanePoke, ElementalStrike
        super().__init__(ManaBolt(), ArcaneSlap(), MagicMissile(), ManaBurst(), ArcanePoke(), ElementalStrike())

class MonsterStance(Stance):
    NAME: str = "monster"
    def __init__(self) -> None:
        from .skill import VenomSlash, ToxicSnap, BlightKick, AcidSpit, NumbingBite, Frenzy
        super().__init__(VenomSlash(), ToxicSnap(), BlightKick(), AcidSpit(), NumbingBite(), Frenzy())

class AndroidStance(Stance):
    NAME: str = "android"
    def __init__(self) -> None:
        from .skill import HydraulicPunch, ShieldBash, Discharge, RechargeProtocol, HeavyHydraulics, Overload
        super().__init__(HydraulicPunch(), ShieldBash(), Discharge(), RechargeProtocol(), HeavyHydraulics(), Overload())

class GlassCannonStance(Stance):
    NAME: str = "glass"
    def __init__(self) -> None:
        from .skill import GlassSliver, CrystalDash, RefractionStrike, BrittleKick, MirrorSlash, ShatterPoint
        super().__init__(GlassSliver(), CrystalDash(), RefractionStrike(), BrittleKick(), MirrorSlash(), ShatterPoint())

class GlassArt(Art):
    NAME: str = "glass resonance"
    def __init__(self) -> None:
        from .skill import ShardShot, MirrorShield, GlassGating, PrismBurst, LensBurst, InfiniteReflection
        super().__init__(ShardShot(), MirrorShield(), GlassGating(), PrismBurst(), LensBurst(), InfiniteReflection())

class CopyArt(Art):
    NAME: str = "mana mimicry"
    def __init__(self) -> None:
        from .skill import PurpleFlame, ManaSiphon, CopySkill, ManaWave, EtherFlash, VesselOverload
        super().__init__(PurpleFlame(), ManaSiphon(), CopySkill(), ManaWave(), EtherFlash(), VesselOverload())

class UnavailableStance(Stance):
    NAME: str = "unavailable"
    def __init__(self) -> None:
        super().__init__()

class UnavailableArmament(Armament):
    NAME: str = "unavailable"
    def __init__(self) -> None:
        super().__init__()