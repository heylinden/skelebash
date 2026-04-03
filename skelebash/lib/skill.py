import typing, random, enum, math


from .style import printStyle, printTypewriter, Style, enterToContinue, printPanel, breakLine
from .animation import Animation, PUNCH_ANIMATION, SLASH_ANIMATION, STRIKE_ANIMATION, EXPLOSION_ANIMATION
from .util import pct, incrpct, decrpct, pct100
from .damagesource import DamageSource
from .effect import HyperarmorEffect

class SkillType(enum.Enum):
    MELEE = "melee"
    HEAVY_MELEE = "heavymelee"
    HEAVIER_MELEE = "heaviermelee"
    RANGED = "ranged"
    HEAVY_RANGED = "heavyranged"
    EXPLOSION = "explosion"
    HEAVY_EXPLOSION = "heavyexplosion"
    OTHER = "other"

class Skill:
    NAME: str = "unnamed skill"
    DESCRIPTION: str = "no description provided."
    MESSAGE: str = "{entity} uses {skill} on {target}!"
    BASE_DAMAGE: int = 0
    BASE_STUN: int = 0 # 0 for combo ender, 1 for combo extender
    EXTRA_DAMAGE_PCT: int = 0 # % damage
    CRIT_CHANCE_PCT: int = 0 # % chance
    CRIT_DAMAGE_PCT: int = 0 # % chance
    WHIFF_CHANCE_PCT: int = 0 # % chance
    ST_COST: int = 0
    MN_COST: int = 0
    STARTUP: int = 5
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 1
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = []
    TYPE: SkillType = SkillType.MELEE
    PARRY_WINDOW: tuple[int, int] | None = None # (min_startup, max_startup)
    SUPER_COST: int = 0
    class Used:
        def __init__(
            self,
            skill: Skill,
            entity: Entity,
            target: Entity,
            interrupted: bool,
            was_interrupted: bool,
            tried_to_be_interrupted: bool,
            whiffed: bool,
            crit: bool,
            damage_dealt: int,
            combo_extendable: bool,
            finisher: bool
        ) -> None:
            self.skill: Skill = skill
            self.entity: Entity = entity
            self.target: Entity = target
            self.interrupted: bool = interrupted
            self.was_interrupted: bool = was_interrupted
            self.tried_to_be_interrupted: bool = tried_to_be_interrupted
            self.whiffed: bool = whiffed
            self.crit: bool = crit
            self.damage_dealt: int = damage_dealt
            self.combo_extendable: bool = combo_extendable
            self.finisher: bool = finisher
    def __init__(self) -> None:
        self.name: str = self.NAME
        self.description: str = self.DESCRIPTION
        self.base_damage: int = self.BASE_DAMAGE
        self.base_stun: int = self.BASE_STUN
        self.extra_damage_pct: int = self.EXTRA_DAMAGE_PCT
        self.crit_chance_pct: int = self.CRIT_CHANCE_PCT
        self.crit_damage_pct: int = self.CRIT_DAMAGE_PCT
        self.whiff_chance_pct: int = self.WHIFF_CHANCE_PCT
        self.st_cost: int = self.ST_COST
        self.mn_cost: int = self.MN_COST
        self.startup: int = self.STARTUP
        self.iframes: bool = self.IFRAMES
        self.hyperarmor: bool = self.HYPERARMOR
        self.locked: bool = self.LOCKED
        self.unlock_at_mastery: int = self.UNLOCK_AT_MASTERY
        self.base_cooldown: int = self.COOLDOWN
        self.active_cooldown: int = self.STARTING_COOLDOWN
        self.animations: list[Animation] = self.ANIMATIONS
        self.message: str = self.MESSAGE
        self.type: SkillType = self.TYPE
        self.parry_window: tuple[int, int] | None = self.PARRY_WINDOW
        self.super_cost: int = self.SUPER_COST
    def showInfo(self, first: bool = False) -> None:
        printPanel(
            f"{Style.BOLD}{Style.REDDISH_PINK if self.super_cost == 100 else ''}{self.name} {Style.BRIGHT_BLACK}[{self.startup}f] ({self.type.value})\n"
            f"{'\n  '.join(self.description.splitlines())}\n"
            f"{Style.YELLOW}{Style.BOLD}  stamina cost: {Style.RESET}{self.st_cost}st  "
            f"{Style.BLUE}{Style.BOLD}mana cost: {Style.RESET}{self.mn_cost}mn  "+\
            f"{Style.REDDISH_PINK}{Style.BOLD}super cost: {Style.RESET}{self.super_cost}%\n"
            f"{Style.RED}{Style.BOLD}  damage: {Style.RESET}{incrpct(self.base_damage, self.extra_damage_pct)} {Style.BRIGHT_BLACK}(base: {self.base_damage})  "
            f"{Style.BRIGHT_ORANGE}{Style.BOLD}stun: {Style.RESET}{self.base_stun}{Style.BRIGHT_BLACK} " + ("(doesn't combo extend)" if not self.base_stun else "(combo extends)")+"\n"
            f"{Style.BRIGHT_BLACK}{Style.BOLD}  active/base cooldown: {Style.RESET}{self.active_cooldown}/{self.base_cooldown} turns",
            (lambda s: printTypewriter(s, delay=0.0001)) if first else printStyle
        )
    def use(self, entity: Entity, target: Entity, disable_whiff: bool = False, disable_crit: bool = False, force_crit: bool = False) -> Skill.Used | None: # type: ignore
        match self.beforeUse(entity, target):
            case "pass":
                printTypewriter(f"* {self.message.format(entity=entity.name, skill=self.name, target=target.name)}")
                damage: int = incrpct(self.base_damage, self.extra_damage_pct)
                damage = incrpct(damage, entity.calculate("strength_pct"))
                damage = decrpct(damage, target.calculate("defense_pct"))
                whiffed: bool = False
                crit: bool = random.randint(1, 100) < (entity.calculate("precision_pct") + self.crit_chance_pct) or force_crit
                if crit and not disable_crit:
                    damage = incrpct(damage, entity.calculate("force_pct") + self.crit_damage_pct)
                    printTypewriter(f"{Style.YELLOW}{Style.BOLD}* critical hit! damage increased by {entity.calculate('force_pct') + self.crit_damage_pct}%")
                else:
                    whiffed: bool = random.randint(1, 100) < (self.whiff_chance_pct + 15) - entity.calculate("concentration_pct")
                if whiffed and not disable_whiff:
                    damage = 0
                    printTypewriter(f"{Style.RED}{Style.BOLD}* whiff! {entity.name} missed!")
                    entity.stun += 1
                
                used: Skill.Used = Skill.Used(
                    skill=self,
                    entity=entity,
                    target=target,
                    interrupted=False,
                    was_interrupted=False,
                    tried_to_be_interrupted=False,
                    whiffed=whiffed,
                    crit=crit,
                    damage_dealt=damage,
                    combo_extendable=self.base_stun >= 1,
                    finisher=damage >= target.hp
                )
                if self.animations:
                    enterToContinue()
                    for animation in self.animations:
                        animation.play()
                printTypewriter(f"* the attack deals {Style.RED}{damage} damage{Style.RESET} to {Style.BRIGHT_GREEN}{target.name}{Style.RESET}!")
                entity.dealDamage(damage, target, (DamageSource.SKILL, used))
                self.afterUse(entity, target, used)
                return used
            case "cancel":
                printTypewriter("<skill cancelled>")
                return None
            case _:
                raise ValueError(f"skill.beforeUse() returned illegal value '{before}'. must be 'pass' or 'cancel'.")
    def beforeUse(self, entity: Entity, target: Entity) -> typing.Literal["pass", "cancel"]: # type: ignore
        return "pass"
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None: # type: ignore
        self.active_cooldown = self.base_cooldown
    def onTick(self, entity: Entity, skelebash: Skelebash) -> None: # type: ignore
        if self.active_cooldown:
            self.active_cooldown -= 1
    def __repr__(self) -> str:
        return f"Skill('{self.name}', {self.base_damage}dmg, {self.base_stun}stun)"

def playOut(player: Entity, player_skill: Skill | None, enemy: Entity, enemy_skill: Skill | None) -> bool: # type: ignore
    if player_skill:
        if player_skill.super_cost > 0:
            if player.super < player_skill.super_cost:
                printTypewriter(f"{Style.RED}not enough super! ({player_skill.super_cost}% required, have {math.floor(player.super)}%){Style.RESET}")
                return False
            player.super -= player_skill.super_cost

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

    if player_skill and isinstance(player_skill, Burst):
        player_skill.use(player, enemy)
        if enemy_skill:
            enemy_skill.use(enemy, player)
        return True
    if enemy_skill and isinstance(enemy_skill, Burst):
        enemy_skill.use(enemy, player)
        if player_skill:
            player_skill.use(player, enemy)
        return True

    if not player_skill:
        enemy_skill.use(enemy, player)
        return True
    if not enemy_skill:
        player_skill.use(player, enemy)
        return True

    def handleBlock(blocker: Entity, blocker_skill: Skill, attacker: Entity, attacker_skill: Skill) -> bool:
        """Returns True if the block/parry was handled, False if it failed."""
        if attacker_skill.type == SkillType.OTHER:
            return False
            
        is_parry: bool = False
        if blocker_skill.parry_window:
            if attacker_skill.startup <= attacker_skill.startup + blocker_skill.parry_window:
                is_parry = True
        
        can_block: bool = False
        if blocker_skill.startup < attacker_skill.startup:
            if isinstance(blocker_skill, (QuickBlock, SlowBlock)):
                if attacker_skill.type in [SkillType.MELEE, SkillType.HEAVY_MELEE, SkillType.HEAVIER_MELEE, SkillType.EXPLOSION, SkillType.HEAVY_EXPLOSION]:
                    can_block = True
                    if attacker_skill.type == SkillType.HEAVIER_MELEE:
                        is_parry = False
            elif isinstance(blocker_skill, Deflect):
                if attacker_skill.type in [SkillType.RANGED, SkillType.HEAVY_RANGED, SkillType.EXPLOSION, SkillType.HEAVY_EXPLOSION]:
                    can_block = True
                    is_parry = False
        
        if not can_block:
            return False

        if is_parry:
            printTypewriter(f"{Style.YELLOW}{Style.BOLD}* parry! {blocker.name} parried {attacker.name}'s {attacker_skill.name}!{Style.RESET}")
            attacker.stun += 2
            return True
        
        break_block = False
        dmg_mult = 0.0
        if attacker_skill.type in [SkillType.HEAVY_MELEE, SkillType.HEAVIER_MELEE, SkillType.HEAVY_RANGED]:
            break_block = True
        elif attacker_skill.type == SkillType.EXPLOSION:
            break_block = True
            dmg_mult = 0.5
        elif attacker_skill.type == SkillType.HEAVY_EXPLOSION:
            break_block = True
            dmg_mult = 1.0

        if break_block:
            printTypewriter(f"{Style.RED}* BLOCK BREAK! {blocker.name} was stunned by the impact!{Style.RESET}")
            blocker.stun += 1
            if dmg_mult > 0:
                 dmg = incrpct(attacker_skill.base_damage, attacker_skill.extra_damage_pct)
                 blocker.takeDamage(round(dmg * dmg_mult), DamageSource.SKILL)
            return True
        else:
            printTypewriter(f"{Style.BRIGHT_BLUE}* {blocker.name} blocked the attack!{Style.RESET}")
            return True

    if isinstance(player_skill, (QuickBlock, SlowBlock, Deflect)):
        if handleBlock(player, player_skill, enemy, enemy_skill):
            return True
    if isinstance(enemy_skill, (QuickBlock, SlowBlock, Deflect)):
        if handleBlock(enemy, enemy_skill, player, player_skill):
             return True

    if player_skill.startup == enemy_skill.startup:
        enterToContinue()
        CLASH_ANIMATION.play()
        printTypewriter(f"{Style.YELLOW}* the attacks clashed!{Style.RESET}")
        player_skill.active_cooldown = player_skill.base_cooldown
        enemy_skill.active_cooldown = enemy_skill.base_cooldown
        return True
    elif player_skill.startup < enemy_skill.startup:
        if enemy_skill.hyperarmor:
            printTypewriter(f"{Style.BRIGHT_BLUE}* {player.name} tries to interrupt {enemy.name} but they're protected by hyperarmor!{Style.RESET}")
            HyperarmorEffect.apply(enemy, 1, 1)
            player_skill.use(player, enemy)
            enemy_skill.active_cooldown = enemy_skill.base_cooldown
            return bool(enemy_skill.use(enemy, player, disable_whiff=True))
        elif enemy_skill.iframes:
            printTypewriter(f"{Style.MAGENTA}* {enemy.name} tries to interrupt {player.name} but they're protected by i-frames!{Style.RESET}")
            enemy_skill.active_cooldown = enemy_skill.base_cooldown
            return bool(enemy_skill.use(enemy, player, disable_whiff=True))
        else:
            printTypewriter(f"{Style.RED}* {player.name} interrupts {enemy.name}! {Style.BRIGHT_BLACK}{player_skill.startup} tick{'s' if player_skill.startup != 1 else ''} < {enemy_skill.startup} tick{'s' if enemy_skill.startup != 1 else ''}{Style.RESET}")
            enemy_skill.active_cooldown = enemy_skill.base_cooldown
            return bool(player_skill.use(player, enemy, disable_whiff=True))
    else:  # enemy_skill.startup < player_skill.startup
        if player_skill.hyperarmor:
            printTypewriter(f"{Style.BRIGHT_BLUE}* {enemy.name} tries to interrupt {player.name} but they're protected by hyperarmor!{Style.RESET}")
            HyperarmorEffect.apply(player, 1, 1)
            enemy_skill.use(enemy, player)
            player_skill.active_cooldown = player_skill.base_cooldown
            return bool(player_skill.use(player, enemy, disable_whiff=True))
        elif player_skill.iframes:
            printTypewriter(f"{Style.MAGENTA}* {enemy.name} tries to interrupt {player.name} but they're protected by i-frames!{Style.RESET}")
            player_skill.active_cooldown = player_skill.base_cooldown
            return bool(player_skill.use(player, enemy, disable_whiff=True))
        else:
            printTypewriter(f"{Style.RED}* {enemy.name} interrupts {player.name}! {Style.BRIGHT_BLACK}{enemy_skill.startup} tick{'s' if enemy_skill.startup != 1 else ''} < {player_skill.startup} tick{'s' if player_skill.startup != 1 else ''}{Style.RESET}")
            player_skill.active_cooldown = player_skill.base_cooldown
            return bool(enemy_skill.use(enemy, player, disable_whiff=True))

class QuickBlock(Skill):
    NAME: str = "quick block"
    DESCRIPTION: str = "a fast block for melee attacks. parries if timed well (4-9 frames)."
    MESSAGE: str = "{entity} readies a quick block."
    STARTUP: int = 4
    PARRY_WINDOW: tuple[int, int] = 5
    TYPE = SkillType.OTHER

class SlowBlock(Skill):
    NAME: str = "slow block"
    DESCRIPTION: str = "a steady block for melee attacks. parries if timed well (14-19 frames)."
    MESSAGE: str = "{entity} readies a slow block."
    STARTUP: int = 14
    PARRY_WINDOW: tuple[int, int] = 5
    TYPE = SkillType.OTHER

class Deflect(Skill):
    NAME: str = "deflect"
    DESCRIPTION: str = "a quick block for ranged attacks."
    MESSAGE: str = "{entity} prepares to deflect."
    STARTUP: int = 4
    TYPE = SkillType.OTHER

class Burst(Skill):
    NAME: str = "burst"
    DESCRIPTION: str = "an instant energy release that consumes 30% super. has i-frames."
    MESSAGE: str = "{entity} BURSTS!"
    STARTUP: int = 0
    IFRAMES: bool = True
    TYPE = SkillType.OTHER
    SUPER_COST = 30

class Rage(Skill):
    NAME: str = "rage"
    DESCRIPTION: str = "a super skill that consumes 100% SUPER. buffs damage by 50% for 3 turns, but also buffs the opponent's damage."
    MESSAGE: str = "{entity} enters a STATE OF RAGE!"
    STARTUP: int = 0
    HYPERARMOR: bool = True
    TYPE: SkillType = SkillType.OTHER
    SUPER_COST: int = 100
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import RageEffect
        RageEffect.apply(entity, 1, 3)
    
class Punch(Skill):
    NAME: str = "punch"
    DESCRIPTION: str = "a weak punch. combo extends."
    MESSAGE: str = "{entity} throws a punch at {target}."
    BASE_DAMAGE: int = 7
    BASE_STUN: int = 1 # 0 for combo ender, 1 for combo extender
    CRIT_CHANCE_PCT: int = 0 # % chance
    CRIT_DAMAGE_PCT: int = 0 # % chance
    WHIFF_CHANCE_PCT: int = 0 # % chance
    ST_COST: int = 0
    MN_COST: int = 0
    STARTUP: int = 5
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 2
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class Slash(Skill):
    NAME: str = "slash"
    DESCRIPTION: str = "a simple slash. combo extends."
    MESSAGE: str = "{entity} slashes at {target}."
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1 # 0 for combo ender, 1 for combo extender
    CRIT_CHANCE_PCT: int = 0 # % chance
    CRIT_DAMAGE_PCT: int = 0 # % chance
    WHIFF_CHANCE_PCT: int = 0 # % chance
    ST_COST: int = 5
    MN_COST: int = 0
    STARTUP: int = 8
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 2
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]
class HeavySlash(Skill):
    NAME: str = "heavy slash"
    DESCRIPTION: str = "a heavy slash that knocks the opponent back."
    MESSAGE: str = "{entity} performs a powerful slash attack on {target}."
    BASE_DAMAGE: int = 18
    BASE_STUN: int = 0 # 0 for combo ender, 1 for combo extender
    CRIT_CHANCE_PCT: int = 0 # % chance
    CRIT_DAMAGE_PCT: int = 0 # % chance
    WHIFF_CHANCE_PCT: int = 0 # % chance
    ST_COST: int = 10
    MN_COST: int = 0
    STARTUP: int = 15
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 3
    STARTING_COOLDOWN: int = 0
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class StickSlap(Skill):
    NAME: str = "stick slap"
    DESCRIPTION: str = "a quick, disrespectful slap with a stick. combo extends."
    MESSAGE: str = "{entity} hits {target} with their stick!"
    BASE_DAMAGE: int = 8
    BASE_STUN: int = 1
    CRIT_CHANCE_PCT: int = 0
    CRIT_DAMAGE_PCT: int = 0
    WHIFF_CHANCE_PCT: int = 0
    ST_COST: int = 3
    MN_COST: int = 0
    STARTUP: int = 10
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]
class FocusDamage(Skill):
    NAME: str = "focus: damage"
    DESCRIPTION: str = "focuses energy on power. massively amplifies the next Art's damage."
    MESSAGE: str = "{entity} focuses on raw power!"
    STARTUP: int = 2
    MN_COST: int = 10
    COOLDOWN: int = 3
    TYPE: SkillType = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        super().afterUse(entity, target, used)
        from .effect import ArtAmplifiedEffect
        eff = ArtAmplifiedEffect.apply(entity, 1, 100)
        eff.boost_type = "damage"
class FocusPrecision(Skill):
    NAME: str = "focus: precision"
    DESCRIPTION: str = "focuses energy on accuracy. massively amplifies the next Art's precision."
    MESSAGE: str = "{entity} focuses on absolute precision!"
    STARTUP: int = 2
    MN_COST: int = 10
    COOLDOWN: int = 3
    TYPE: SkillType = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        super().afterUse(entity, target, used)
        from .effect import ArtAmplifiedEffect
        eff = ArtAmplifiedEffect.apply(entity, 1, 100)
        eff.boost_type = "precision"
class FocusCritical(Skill):
    NAME: str = "focus: critical"
    DESCRIPTION: str = "focuses energy on weak points. massively amplifies the next Art's critical damage."
    MESSAGE: str = "{entity} focuses on lethal strikes!"
    STARTUP: int = 2
    MN_COST: int = 10
    COOLDOWN: int = 3
    TYPE: SkillType = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        super().afterUse(entity, target, used)
        from .effect import ArtAmplifiedEffect
        eff = ArtAmplifiedEffect.apply(entity, 1, 100)
        eff.boost_type = "critical"
class FocusStamina(Skill):
    NAME: str = "focus: stamina"
    DESCRIPTION: str = "focuses energy on flow. the next Art will cost no stamina."
    MESSAGE: str = "{entity} focuses on effortless movement!"
    STARTUP: int = 2
    MN_COST: int = 10
    COOLDOWN: int = 3
    TYPE: SkillType = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        super().afterUse(entity, target, used)
        from .effect import ArtAmplifiedEffect
        eff = ArtAmplifiedEffect.apply(entity, 1, 100)
        eff.boost_type = "stamina"
class UltimateFocus(Skill):
    NAME: str = "ULTIMATE FOCUS"
    DESCRIPTION: str = "A SUPER skill that consumes 100% SUPER. Amplifies EVERYTHING for the next Art."
    MESSAGE: str = "{entity} REACHES ULTIMATE FOCUS!"
    STARTUP: int = 0
    COOLDOWN: int = 3
    TYPE: SkillType = SkillType.OTHER
    SUPER_COST: int = 100
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        super().afterUse(entity, target, used)
        from .effect import ArtAmplifiedEffect
        eff = ArtAmplifiedEffect.apply(entity, 1, 100)
        eff.boost_type = "all"