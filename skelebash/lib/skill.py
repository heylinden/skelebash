from __future__ import annotations
import typing, random


from .animation import CLASH_ANIMATION, PUNCH_ANIMATION
from .style import printStyle, printTypewriter, Style, enterToContinue, printPanel, breakLine
from .animation import Animation
from .util import pct
from .damagesource import DamageSource
from .effect import HyperarmorEffect

class Skill:
    NAME: str = "unnamed skill"
    DESCRIPTION: str = "no description provided."
    MESSAGE: str = "{entity} uses {skill} on {target}!"
    BASE_DAMAGE: int = 1
    BASE_STUN: int = 0 # 0 for combo ender, 1 for combo extender
    CRIT_CHANCE_PCT: int = 25 # % chance
    WHIFF_CHANCE_PCT: int = 25 # % chance
    ST_COST: int = 0
    MN_COST: int = 0
    STARTUP: int = 5
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 1
    STARTING_COOLDOWN: int = 0
    ANIMATION: Animation | None = None
    class Used:
        def __init__(
            self,
            skill: Skill,
            interrupted: bool,
            was_interrupted: bool,
            tried_to_be_interrupted: bool,
            whiffed: bool,
            crit: bool,
            damage_dealt: int,
            stun_dealt: int,
            combo_extendable: bool,
            finisher: bool
        ) -> None:
            self.skill: Skill = skill
            self.interrupted: bool = interrupted
            self.was_interrupted: bool = was_interrupted
            self.tried_to_be_interrupted: bool = tried_to_be_interrupted
            self.whiffed: bool = whiffed
            self.crit: bool = crit
            self.damage_dealt: int = damage_dealt
            self.stun_dealt: int = stun_dealt
            self.combo_extendable: bool = combo_extendable
            self.finisher: bool = finisher
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.base_damage: int = self.BASE_DAMAGE
        self.damage: int = self.base_damage
        self.base_stun: int = self.BASE_STUN
        self.st_cost: int = self.ST_COST
        self.mn_cost: int = self.MN_COST
        self.startup: int = self.STARTUP
        self.iframes: bool = self.IFRAMES
        self.hyperarmor: bool = self.HYPERARMOR
        self.locked: bool = self.LOCKED
        self.unlock_at_mastery: int = self.UNLOCK_AT_MASTERY
        self.base_cooldown: int = self.COOLDOWN
        self.active_cooldown: int = self.STARTING_COOLDOWN
        self.animation: Animation | None = self.ANIMATION
        self.message: str = self.MESSAGE
    def showInfo(self, first: bool = False) -> None:
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"skill {Style.BOLD}{self.name}{Style.RESET} [{self.animation.name if self.animation else "other"}]")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.BOLD}  description: {Style.RESET}{'\n  '.join(self.description.splitlines())}")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.YELLOW}{Style.BOLD}  stamina cost: {Style.RESET}{self.st_cost}st")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.BLUE}{Style.BOLD}  mana cost: {Style.RESET}{self.mn_cost}mn")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.BRIGHT_BLACK}  ---")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.RED}{Style.BOLD}  damage: {Style.RESET}{self.damage}")
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.BRIGHT_ORANGE}{Style.BOLD}  base stun: {Style.RESET}{self.base_stun}{Style.BRIGHT_BLACK} " + ("(doesn't combo extend)" if not self.base_stun else "(combo extends)"))
        ((lambda text: printTypewriter(text, 0.0005) )if first else printStyle)(f"{Style.BRIGHT_BLACK}{Style.BOLD}  active/base cooldown: {Style.RESET}{self.active_cooldown}/{self.base_cooldown} turns")
    def use(self, entity: Entity, target: Entity) -> Skill.Used | None: # type: ignore
        match self.beforeUse(entity, target):
            case "pass":
                printTypewriter(f"* {self.message.format(entity=entity.name, skill=self.name, target=target.name)}")
                additional_messages: list[str] = []
                damage: int = pct(self.damage, 100 + entity.calculate("strength_pct"))
                damage -= pct(damage, target.calculate("defense_pct"))
                whiffed: bool = random.randint(1, 100) < 15 - entity.calculate("concentration_pct")
                if whiffed:
                    damage = 0
                    printTypewriter(f"{Style.RED}{Style.BOLD}* whiff! {entity.name} missed!")
                    additional_messages.append("*0")
                    entity.stun += 1
                crit: bool = random.randint(1, 100) < entity.calculate("precision_pct")
                if crit:
                    damage += pct(damage, entity.calculate("force_pct"))
                    printTypewriter(f"{Style.YELLOW}{Style.BOLD}* critical hit! damage increased by {entity.calculate('force_pct')}%")
                    additional_messages.append(f"*(1+force_pct<{entity.calculate('force_pct')}%>)")
                entity.dealDamage(damage, target, (DamageSource.SKILL, self))
                used: Skill.Used = Skill.Used(
                    skill=self,
                    interrupted=False,
                    was_interrupted=False,
                    tried_to_be_interrupted=False,
                    whiffed=whiffed,
                    crit=crit,
                    damage_dealt=damage,
                    stun_dealt=self.base_stun,
                    combo_extendable=self.base_stun >= 1,
                    finisher=damage >= target.hp
                )
                enterToContinue()
                self.afterUse(entity, target, used)
                printTypewriter(f"* the attack deals {Style.RED}{damage} damage{Style.RESET} to {Style.BRIGHT_GREEN}{target.name}{Style.RESET}!")
                printStyle(
                    f"{Style.BRIGHT_BLACK}damage<{damage}> = "
                    f"base_damage<{self.damage}>"
                    f"*(1+entity_strength<{entity.calculate('strength_pct')}%>)"
                    f"*(1-target_defense<{target.calculate('defense_pct')}%>)"
                    +"".join(additional_messages)
                )
                return used
            case "cancel":
                printTypewriter("<skill cancelled>")
                return None
            case _:
                raise ValueError(f"skill.beforeUse() returned illegal value '{before}'. must be 'pass' or 'cancel'.")
    def beforeUse(self, entity: Entity, target: Entity) -> typing.Literal["pass", "cancel"]: # type: ignore
        if self.active_cooldown >= 1:
            printTypewriter(f"{Style.RED}skill on cooldown for {self.active_cooldown} more turns.")
        if entity.st < self.st_cost:
            printTypewriter(f"{Style.RED}not enough stamina.")
            return "cancel"
        if entity.mn < self.mn_cost:
            printTypewriter(f"{Style.RED}not enough mana.")
            return "cancel"
        entity.st -= self.st_cost
        entity.mn -= self.mn_cost
        return "pass"
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None: # type: ignore
        self.active_cooldown = self.base_cooldown
        if self.animation:
            self.animation.play()
    
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        self.active_cooldown -= 1
    def __repr__(self) -> str:
        return f"Skill('{self.name}', {self.damage}dmg, {self.base_stun}stun)"

def playOut(player: Entity, player_skill: Skill | None, enemy: Entity, enemy_skill: Skill | None) -> bool: # type: ignore
    if player_skill:
        printPanel(f"{player.name} used {player_skill.name}!")
        breakLine()
    else:
        printPanel(f"{player.name} passes their turn.")
        breakLine()
    if enemy_skill:
        printPanel(f"{enemy.name} used {enemy_skill.name}!")
        breakLine()
    else:
        printPanel(f"{enemy.name} passes their turn.")
        breakLine()

    if not player_skill and not enemy_skill:
        return True
    if not player_skill:
        enemy_skill.use(enemy, player)
        return True
    if not enemy_skill:
        player_skill.use(player, enemy)
        return True
    if abs(player_skill.startup - enemy_skill.startup):
        enterToContinue()
        CLASH_ANIMATION.play()
        printTypewriter(f"{Style.YELLOW}* the attacks clashed!{Style.RESET}")
        player_skill.active_cooldown = 2
        enemy_skill.active_cooldown = 2
        return True
    elif player_skill.startup < enemy_skill.startup:
        if enemy_skill.hyperarmor:
            printTypewriter(f"{Style.BRIGHT_BLUE}* {player.name} tries to interrupt {enemy.name} but they're protected by hyperarmor!{Style.RESET}")
            HyperarmorEffect.apply(enemy, 1, 1)
            player_skill.use(player, enemy)
            return bool(enemy_skill.use(enemy, player))
        elif enemy_skill.iframes:
            printTypewriter(f"{Style.MAGENTA}* {enemy.name} tries to interrupt {player.name} but they're protected by i-frames!{Style.RESET}")
            return bool(enemy_skill.use(enemy, player))
        else:
            printTypewriter(f"{Style.RED}* {player.name} interrupts {enemy.name}! {Style.BRIGHT_BLACK}{player_skill.startup} tick{'s' if player_skill.startup != 1 else ''} < {enemy_skill.startup} tick{'s' if enemy_skill.startup != 1 else ''}{Style.RESET}")
            return bool(player_skill.use(player, enemy))
    else:  # enemy_skill.startup < player_skill.startup
        if player_skill.hyperarmor:
            printTypewriter(f"{Style.BRIGHT_BLUE}* {enemy.name} tries to interrupt {player.name} but they're protected by hyperarmor!{Style.RESET}")
            HyperarmorEffect.apply(player, 1, 1)
            enemy_skill.use(enemy, player)
            return bool(player_skill.use(player, enemy))
        elif player_skill.iframes:
            printTypewriter(f"{Style.MAGENTA}* {enemy.name} tries to interrupt {player.name} but they're protected by i-frames!{Style.RESET}")
            return bool(player_skill.use(player, enemy))
        else:
            printTypewriter(f"{Style.RED}* {enemy.name} interrupts {player.name}! {Style.BRIGHT_BLACK}{enemy_skill.startup} tick{'s' if enemy_skill.startup != 1 else ''} < {player_skill.startup} tick{'s' if player_skill.startup != 1 else ''}{Style.RESET}")
            return bool(enemy_skill.use(enemy, player))
    
class Punch(Skill):
    NAME: str = "punch"
    DESCRIPTION: str = "a weak punch. combo extends."
    MESSAGE: str = "{entity} throws a punch at {target}."
    BASE_DAMAGE: int = 7
    BASE_STUN: int = 1 # 0 for combo ender, 1 for combo extender
    CRIT_CHANCE_PCT: int = 25 # % chance
    WHIFF_CHANCE_PCT: int = 25 # % chance
    ST_COST: int = 0
    MN_COST: int = 0
    STARTUP: int = 5
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 2
    STARTING_COOLDOWN: int = 0
    ANIMATION: Animation = PUNCH_ANIMATION