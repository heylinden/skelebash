import typing, random, enum, math, os, time, sys


from .style import printStyle, printTypewriter, Style, enterToContinue, printPanel, breakLine, printStyleInline
from .animation import Animation, PUNCH_ANIMATION, SLASH_ANIMATION, STRIKE_ANIMATION, EXPLOSION_ANIMATION, KICK_ANIMATION, CLASH_ANIMATION
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

    if player_skill and isinstance(player_skill, (Burst, Taunt)):
        player_skill.use(player, enemy)
        if enemy_skill:
            enemy_skill.use(enemy, player)
        return True
    if enemy_skill and isinstance(enemy_skill, (Burst, Taunt)):
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
    TYPE: SkillType = SkillType.OTHER

class QuickBlockNoParry(Skill):
    NAME: str = "quick block"
    DESCRIPTION: str = "a fast block for melee attacks."
    MESSAGE: str = "{entity} readies a quick block."
    STARTUP: int = 4
    PARRY_WINDOW: tuple[int, int] = 0
    TYPE: SkillType = SkillType.OTHER

class SlowBlock(Skill):
    NAME: str = "slow block"
    DESCRIPTION: str = "a steady block for melee attacks. parries if timed well (14-19 frames)."
    MESSAGE: str = "{entity} readies a slow block."
    STARTUP: int = 14
    PARRY_WINDOW: tuple[int, int] = 5
    TYPE: SkillType = SkillType.OTHER

class SlowBlockNoParry(Skill):
    NAME: str = "slow block"
    DESCRIPTION: str = "a steady block for melee attacks."
    MESSAGE: str = "{entity} readies a slow block."
    STARTUP: int = 14
    PARRY_WINDOW: tuple[int, int] = 0
    TYPE: SkillType = SkillType.OTHER

class Deflect(Skill):
    NAME: str = "deflect"
    DESCRIPTION: str = "a quick block for ranged attacks."
    MESSAGE: str = "{entity} prepares to deflect."
    STARTUP: int = 4
    TYPE: SkillType = SkillType.OTHER

class Burst(Skill):
    NAME: str = "burst"
    DESCRIPTION: str = "an instant energy release that consumes 30% super. has i-frames."
    MESSAGE: str = "{entity} BURSTS!"
    STARTUP: int = 0
    IFRAMES: bool = True
    TYPE: SkillType = SkillType.OTHER
    SUPER_COST: int = 30
    COOLDOWN: int = 2

class Rage(Skill):
    NAME: str = "rage"
    DESCRIPTION: str = "a super skill that consumes 100% SUPER. buffs damage by 50% for 3 turns, but also buffs the opponent's damage."
    MESSAGE: str = "{entity} enters a STATE OF RAGE!"
    STARTUP: int = 0
    HYPERARMOR: bool = True
    TYPE: SkillType = SkillType.OTHER
    SUPER_COST: int = 100
    STARTING_COOLDOWN: int = 6
    COOLDOWN: int = 6
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import RageEffect
        RageEffect.apply(entity, 1, 3)
    
class Taunt(Skill):
    NAME: str = "taunt"
    DESCRIPTION: str = "taunt the enemy to double your super gain, but you take 50% more damage for 3 turns."
    MESSAGE: str = "{entity} is taunting {target}!"
    STARTUP: int = 0
    COOLDOWN: int = 6
    STARTING_COOLDOWN: int = 6
    HYPERARMOR: bool = True
    TYPE: SkillType = SkillType.OTHER

    def use(self, entity: Entity, target: Entity, **kwargs) -> Skill.Used:
        taunt_dialogues = getattr(entity, "TAUNT_DIALOGUES", [
            [("entity", "you're nothing."), ("target", "..."), ("entity", "heh.")],
            [("target", "surrender, you're not winning this..."), ("entity", "you talk too much."), ("entity", "just shut up and fight.")],
            [("entity", "i'll cut you into pieces!"), ("target", "try me!"), ("entity", "oh i will.")],
            [("entity", "i thought you were going to be better..."), ("target", "oh don't you mock me!"), ("entity", "heh.")],
        ])
        dialogue = random.choice(taunt_dialogues)
        for speaker_id, text in dialogue:
            if speaker_id == "entity":
                printTypewriter(f"* {Style.BRIGHT_ORANGE}{entity.name}{Style.BRIGHT_BLACK}:{Style.RESET} {text}")
                if "--fast" not in sys.argv: time.sleep(1)
            else:
                printStyleInline(' ' * (os.get_terminal_size().columns//2))
                printTypewriter(f"{Style.BRIGHT_BLUE}{target.name}{Style.BRIGHT_BLACK}:{Style.RESET} {text} *")
                if "--fast" not in sys.argv: time.sleep(1)
        
        from .effect import TauntEffect
        TauntEffect.apply(entity, 1, 3)
        return Skill.Used(
            skill=self,
            entity=entity,
            target=target,
            interrupted=False,
            was_interrupted=False,
            tried_to_be_interrupted=False,
            whiffed=False,
            crit=False,
            damage_dealt=0,
            combo_extendable=False,
            finisher=False
        )

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

# --- STANCE SKILLS ---

# BALANCED
class Kick(Skill):
    NAME: str = "kick"
    DESCRIPTION: str = "a basic kick. moderate damage and startup."
    MESSAGE: str = "{entity} kicks {target}."
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    ST_COST: int = 3
    STARTUP: int = 7
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [KICK_ANIMATION]

class Hook(Skill):
    NAME: str = "hook"
    DESCRIPTION: str = "a quick hook punch. slightly faster than a regular punch."
    MESSAGE: str = "{entity} hooks {target}!"
    BASE_DAMAGE: int = 9
    BASE_STUN: int = 1
    ST_COST: int = 2
    STARTUP: int = 6
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class Uppercut(Skill):
    NAME: str = "uppercut"
    DESCRIPTION: str = "a powerful rising punch that deals good stun."
    MESSAGE: str = "{entity} delivers a sharp uppercut to {target}!"
    BASE_DAMAGE: int = 12
    BASE_STUN: int = 1
    ST_COST: int = 5
    STARTUP: int = 8
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class RoundhouseKick(Skill):
    NAME: str = "roundhouse kick"
    DESCRIPTION: str = "a powerful spinning kick with high damage."
    MESSAGE: str = "{entity} roundhouses {target}!"
    BASE_DAMAGE: int = 18
    BASE_STUN: int = 1
    ST_COST: int = 8
    STARTUP: int = 12
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [KICK_ANIMATION]

class Tackle(Skill):
    NAME: str = "tackle"
    DESCRIPTION: str = "a basic tackle that closes distance and stuns."
    MESSAGE: str = "{entity} tackles {target}!"
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    ST_COST: int = 4
    STARTUP: int = 10
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

# NINJA
class QuickStrike(Skill):
    NAME: str = "quick strike"
    DESCRIPTION: str = "a very fast strike with low damage."
    MESSAGE: str = "{entity} strikes {target} with incredible speed."
    BASE_DAMAGE: int = 5
    BASE_STUN: int = 1
    ST_COST: int = 2
    STARTUP: int = 3
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class DoubleTap(Skill):
    NAME: str = "double tap"
    DESCRIPTION: str = "a rapid two-hit combo."
    MESSAGE: str = "{entity} taps {target} twice."
    BASE_DAMAGE: int = 8
    BASE_STUN: int = 1
    ST_COST: int = 4
    STARTUP: int = 4
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class TripleStrike(Skill):
    NAME: str = "triple strike"
    DESCRIPTION: str = "a rapid three-hit combo that deals moderate damage."
    MESSAGE: str = "{entity} unleashes a triple strike on {target}!"
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    ST_COST: int = 6
    STARTUP: int = 5
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class BackflipKick(Skill):
    NAME: str = "backflip kick"
    DESCRIPTION: str = "a quick acrobatic kick with fast recovery."
    MESSAGE: str = "{entity} performs a backflip kick on {target}!"
    BASE_DAMAGE: int = 7
    BASE_STUN: int = 1
    ST_COST: int = 3
    STARTUP: int = 4
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [KICK_ANIMATION]

class ShadowStrike(Skill):
    NAME: str = "shadow strike"
    DESCRIPTION: str = "an extremely fast strike from the shadows. expensive but lethal."
    MESSAGE: str = "{entity} strikes from the shadows!"
    BASE_DAMAGE: int = 12
    BASE_STUN: int = 1
    ST_COST: int = 10
    STARTUP: int = 2
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class DaggerThrow(Skill):
    NAME: str = "dagger throw"
    DESCRIPTION: str = "a quick ranged attack with a hidden dagger."
    MESSAGE: str = "{entity} throws a dagger at {target}!"
    BASE_DAMAGE: int = 5
    BASE_STUN: int = 0
    ST_COST: int = 2
    STARTUP: int = 4
    COOLDOWN: int = 1
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

# WARRIOR
class HeavyStrike(Skill):
    NAME: str = "heavy strike"
    DESCRIPTION: str = "a slow but powerful strike with hyperarmor."
    MESSAGE: str = "{entity} strikes {target} with crushing force!"
    BASE_DAMAGE: int = 25
    BASE_STUN: int = 1
    ST_COST: int = 12
    STARTUP: int = 15
    HYPERARMOR: bool = True
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class CrushingBlow(Skill):
    NAME: str = "crushing blow"
    DESCRIPTION: str = "an extremely heavy attack that ignores defense but is very slow. has hyperarmor."
    MESSAGE: str = "{entity} UNLEASHES A CRUSHING BLOW ON {target}!"
    BASE_DAMAGE: int = 35
    BASE_STUN: int = 0
    ST_COST: int = 18
    STARTUP: int = 22
    HYPERARMOR: bool = True
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class ShoulderBash(Skill):
    NAME: str = "shoulder bash"
    DESCRIPTION: str = "a heavy shoulder bash that utilizes hyperarmor. faster than most warrior moves."
    MESSAGE: str = "{entity} bashes {target} with their shoulder!"
    BASE_DAMAGE: int = 15
    BASE_STUN: int = 1
    ST_COST: int = 8
    STARTUP: int = 10
    HYPERARMOR: bool = True
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class OverheadSwing(Skill):
    NAME: str = "overhead swing"
    DESCRIPTION: str = "a slow overhead strike with massive weight. has hyperarmor."
    MESSAGE: str = "{entity} swings down on {target}!"
    BASE_DAMAGE: int = 28
    BASE_STUN: int = 0
    ST_COST: int = 15
    STARTUP: int = 18
    HYPERARMOR: bool = True
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class GreatSwing(Skill):
    NAME: str = "great swing"
    DESCRIPTION: str = "a wide, sweeping swing with hyperarmor."
    MESSAGE: str = "{entity} performs a great swing against {target}!"
    BASE_DAMAGE: int = 22
    BASE_STUN: int = 1
    ST_COST: int = 12
    STARTUP: int = 14
    HYPERARMOR: bool = True
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class Brace(Skill):
    NAME: str = "brace"
    DESCRIPTION: str = "a defensive stance that provides hyperarmor. doesn't deal much damage but protects the user."
    MESSAGE: str = "{entity} braces for impact!"
    BASE_DAMAGE: int = 2
    BASE_STUN: int = 0
    ST_COST: int = 5
    STARTUP: int = 2
    HYPERARMOR: bool = True
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

# SORCERER
class ManaBolt(Skill):
    NAME: str = "mana bolt"
    DESCRIPTION: str = "a weak bolt of pure mana. normal startup."
    MESSAGE: str = "{entity} fires a mana bolt at {target}."
    BASE_DAMAGE: int = 6
    BASE_STUN: int = 1
    MN_COST: int = 5
    STARTUP: int = 8
    COOLDOWN: int = 2
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class ArcaneSlap(Skill):
    NAME: str = "arcane slap"
    DESCRIPTION: str = "a weak physical slap imbued with mana. normal startup."
    MESSAGE: str = "{entity} slaps {target} with arcane energy!"
    BASE_DAMAGE: int = 5
    BASE_STUN: int = 1
    MN_COST: int = 2
    STARTUP: int = 8
    COOLDOWN: int = 1
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class MagicMissile(Skill):
    NAME: str = "magic missile"
    DESCRIPTION: str = "fires a barrage of magical missiles. deals moderate damage at range."
    MESSAGE: str = "{entity} fires magic missiles at {target}!"
    BASE_DAMAGE: int = 12
    BASE_STUN: int = 1
    MN_COST: int = 10
    STARTUP: int = 10
    COOLDOWN: int = 4
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class ManaBurst(Skill):
    NAME: str = "mana burst"
    DESCRIPTION: str = "an explosion of mana that deals significant damage."
    MESSAGE: str = "{entity} releases a mana burst!"
    BASE_DAMAGE: int = 18
    BASE_STUN: int = 0
    MN_COST: int = 15
    STARTUP: int = 12
    COOLDOWN: int = 5
    TYPE = SkillType.EXPLOSION
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class ArcanePoke(Skill):
    NAME: str = "arcane poke"
    DESCRIPTION: str = "a quick, low-cost poke with magical energy."
    MESSAGE: str = "{entity} pokes {target} with arcane power!"
    BASE_DAMAGE: int = 4
    BASE_STUN: int = 1
    MN_COST: int = 1
    STARTUP: int = 6
    COOLDOWN: int = 1
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class ElementalStrike(Skill):
    NAME: str = "elemental strike"
    DESCRIPTION: str = "a mana-infused strike that deals moderate damage."
    MESSAGE: str = "{entity} strikes {target} with elemental force!"
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    MN_COST: int = 8
    STARTUP: int = 10
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

# MONSTER
class VenomSlash(Skill):
    NAME: str = "venom slash"
    DESCRIPTION: str = "a quick slash that applies poison. fast startup."
    MESSAGE: str = "{entity} slashes {target} with venomous claws!"
    BASE_DAMAGE: int = 6
    BASE_STUN: int = 1
    ST_COST: int = 3
    STARTUP: int = 5
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import PoisonEffect
        PoisonEffect.apply(target, 2, 3)

class ToxicSnap(Skill):
    NAME: str = "toxic snap"
    DESCRIPTION: str = "a moderate strike that applies strong poison."
    MESSAGE: str = "{entity} snaps at {target} with toxic fangs!"
    BASE_DAMAGE: int = 8
    BASE_STUN: int = 1
    ST_COST: int = 5
    STARTUP: int = 8
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import PoisonEffect
        PoisonEffect.apply(target, 4, 3)

class BlightKick(Skill):
    NAME: str = "blight kick"
    DESCRIPTION: str = "a powerful kick that spreads a blight, damaging and poisoning the target."
    MESSAGE: str = "{entity} kicks {target} with a blighted leg!"
    BASE_DAMAGE: int = 15
    BASE_STUN: int = 1
    ST_COST: int = 8
    STARTUP: int = 10
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [KICK_ANIMATION]
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import PoisonEffect
        PoisonEffect.apply(target, 3, 3)

class AcidSpit(Skill):
    NAME: str = "acid spit"
    DESCRIPTION: str = "a ranged acid attack that deals low damage but high poison."
    MESSAGE: str = "{entity} spits acid at {target}!"
    BASE_DAMAGE: int = 4
    BASE_STUN: int = 0
    ST_COST: int = 4
    STARTUP: int = 7
    COOLDOWN: int = 2
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import PoisonEffect
        PoisonEffect.apply(target, 5, 3)

class NumbingBite(Skill):
    NAME: str = "numbing bite"
    DESCRIPTION: str = "a bite that numbs the target, increasing their stun."
    MESSAGE: str = "{entity} sinks their fangs into {target}!"
    BASE_DAMAGE: int = 5
    BASE_STUN: int = 3
    ST_COST: int = 4
    STARTUP: int = 6
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class Frenzy(Skill):
    NAME: str = "frenzy"
    DESCRIPTION: str = "a rapid series of wild claw swipes."
    MESSAGE: str = "{entity} goes into a frenzy against {target}!"
    BASE_DAMAGE: int = 18
    BASE_STUN: int = 0
    ST_COST: int = 10
    STARTUP: int = 12
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION@0.005, STRIKE_ANIMATION@0.005]*7


# ANDROID
class HydraulicPunch(Skill):
    NAME: str = "hydraulic punch"
    DESCRIPTION: str = "a powerful punch fueled by high pressure. high charge cost."
    MESSAGE: str = "{entity} delivers a hydraulic punch to {target}!"
    BASE_DAMAGE: int = 28
    BASE_STUN: int = 1
    ST_COST: int = 25
    STARTUP: int = 12
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [PUNCH_ANIMATION]

class ShieldBash(Skill):
    NAME: str = "shield bash"
    DESCRIPTION: str = "a heavy bash with integrated shielding. has hyperarmor."
    MESSAGE: str = "{entity} bashes {target} with their reinforced arm!"
    BASE_DAMAGE: int = 20
    BASE_STUN: int = 0
    ST_COST: int = 20
    STARTUP: int = 15
    HYPERARMOR: bool = True
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class Discharge(Skill):
    NAME: str = "discharge"
    DESCRIPTION: str = "releases accumulated heat as a shockwave. deals explosion damage."
    MESSAGE: str = "{entity} discharges energy at {target}!"
    BASE_DAMAGE: int = 22
    BASE_STUN: int = 0
    ST_COST: int = 15
    STARTUP: int = 10
    COOLDOWN: int = 5
    TYPE = SkillType.EXPLOSION
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class RechargeProtocol(Skill):
    NAME: str = "recharge"
    DESCRIPTION: str = "temporarily diverts power to core systems. restores charge."
    MESSAGE: str = "{entity} initiates recharge protocol."
    BASE_DAMAGE: int = 0
    BASE_STUN: int = 0
    ST_COST: int = 0
    STARTUP: int = 5
    COOLDOWN: int = 3
    TYPE = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        entity.healStamina(30)
        printTypewriter(f"{Style.BRIGHT_BLUE}* restored 30 {entity.ST_LABEL}!{Style.RESET}")

class HeavyHydraulics(Skill):
    NAME: str = "heavy hydraulics"
    DESCRIPTION: str = "the heaviest hit available for androids. massive damage and charge cost."
    MESSAGE: str = "{entity} CRUSHES {target} with heavy hydraulics!"
    BASE_DAMAGE: int = 45
    BASE_STUN: int = 0
    ST_COST: int = 40
    STARTUP: int = 22
    HYPERARMOR: bool = True
    COOLDOWN: int = 6
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class Overload(Skill):
    NAME: str = "overload"
    DESCRIPTION: str = "releases all safeties for a massive hit, but stuns the user."
    MESSAGE: str = "{entity} OVERLOADS their core to strike {target}!"
    BASE_DAMAGE: int = 60
    BASE_STUN: int = 2
    ST_COST: int = 50
    STARTUP: int = 25
    HYPERARMOR: bool = True
    COOLDOWN: int = 8
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        printTypewriter(f"{Style.RED}* core overheat! {entity.name} is stunned!{Style.RESET}")
        entity.stun += 2


# GLASS CANNON

# STANCE
class GlassSliver(Skill):
    NAME: str = "glass sliver"
    DESCRIPTION: str = "a quick, sharp jab with a shard of glass."
    MESSAGE: str = "{entity} jabs {target} with a glass sliver!"
    BASE_DAMAGE: int = 10
    BASE_STUN: int = 1
    ST_COST: int = 3
    STARTUP: int = 4
    COOLDOWN: int = 1
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class CrystalDash(Skill):
    NAME: str = "crystal dash"
    DESCRIPTION: str = "a quick dash forward with glass protection. has iframes."
    MESSAGE: str = "{entity} dashes through {target} in a flash of crystal!"
    BASE_DAMAGE: int = 14
    BASE_STUN: int = 1
    ST_COST: int = 6
    STARTUP: int = 6
    IFRAMES: bool = True
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class RefractionStrike(Skill):
    NAME: str = "refraction strike"
    DESCRIPTION: str = "a strike that bends light to hit a vulnerable spot. high crit chance."
    MESSAGE: str = "{entity} strikes {target} through a refracted light!"
    BASE_DAMAGE: int = 16
    BASE_STUN: int = 1
    ST_COST: int = 8
    STARTUP: int = 9
    CRIT_CHANCE_PCT: int = 40
    COOLDOWN: int = 3
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class BrittleKick(Skill):
    NAME: str = "brittle kick"
    DESCRIPTION: str = "a heavy kick that shatters on impact, dealing bonus damage."
    MESSAGE: str = "{entity} delivers a brittle but heavy kick to {target}!"
    BASE_DAMAGE: int = 24
    BASE_STUN: int = 0
    ST_COST: int = 10
    STARTUP: int = 15
    COOLDOWN: int = 5
    ANIMATIONS: list[Animation] = [KICK_ANIMATION]

class MirrorSlash(Skill):
    NAME: str = "mirror slash"
    DESCRIPTION: str = "a clean slash that reflects the target's image."
    MESSAGE: str = "{entity} slashes {target} with a mirrored blade!"
    BASE_DAMAGE: int = 18
    BASE_STUN: int = 1
    ST_COST: int = 7
    STARTUP: int = 7
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION]

class ShatterPoint(Skill):
    NAME: str = "shatter point"
    DESCRIPTION: str = "a precise strike aimed at the target's weakest point."
    MESSAGE: str = "{entity} strikes the shatter point of {target}!"
    BASE_DAMAGE: int = 35
    BASE_STUN: int = 0
    ST_COST: int = 20
    STARTUP: int = 20
    HYPERARMOR: bool = True
    COOLDOWN: int = 6
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

# ART
class ShardShot(Skill):
    NAME: str = "shard shot"
    DESCRIPTION: str = "fires a sharp glass shard at the target. low mana cost."
    MESSAGE: str = "{entity} fires a glass shard at {target}!"
    BASE_DAMAGE: int = 12
    BASE_STUN: int = 1
    MN_COST: int = 5
    STARTUP: int = 8
    COOLDOWN: int = 2
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [STRIKE_ANIMATION]

class MirrorShield(Skill):
    NAME: str = "mirror shield"
    DESCRIPTION: str = "creates a thin shield of glass that perfect blocks one attack."
    MESSAGE: str = "{entity} manifests a mirror shield!"
    BASE_DAMAGE: int = 0
    BASE_STUN: int = 0
    MN_COST: int = 10
    STARTUP: int = 4
    COOLDOWN: int = 5
    TYPE = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        from .effect import GlassShieldEffect
        GlassShieldEffect.apply(entity, 1, 10)

class GlassGating(Skill):
    NAME: str = "glass gating"
    DESCRIPTION: str = "summons multiple glass panes to crush the target. heavy damage."
    MESSAGE: str = "{entity} gates {target} between glass panes!"
    BASE_DAMAGE: int = 32
    BASE_STUN: int = 0
    MN_COST: int = 15
    STARTUP: int = 14
    COOLDOWN: int = 4
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class PrismBurst(Skill):
    NAME: str = "prism burst"
    DESCRIPTION: str = "shatters a prism, sending glass shards in all directions."
    MESSAGE: str = "{entity} shatters a prism around {target}!"
    BASE_DAMAGE: int = 24
    BASE_STUN: int = 0
    MN_COST: int = 12
    STARTUP: int = 10
    COOLDOWN: int = 4
    TYPE = SkillType.EXPLOSION
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class LensBurst(Skill):
    NAME: str = "lens burst"
    DESCRIPTION: str = "concentrates mana through a glass lens for a powerful beam."
    MESSAGE: str = "{entity} fires a lens-intensified burst at {target}!"
    BASE_DAMAGE: int = 28
    BASE_STUN: int = 1
    MN_COST: int = 20
    STARTUP: int = 12
    COOLDOWN: int = 4
    TYPE = SkillType.RANGED
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class InfiniteReflection(Skill):
    NAME: str = "super: infinite reflection"
    DESCRIPTION: str = "summons an array of mirrors that strike the target from all sides."
    MESSAGE: str = "{entity} unleashes INFINITE REFLECTION on {target}!"
    BASE_DAMAGE: int = 50
    BASE_STUN: int = 0
    MN_COST: int = 0
    SUPER_COST: int = 100
    STARTUP: int = 10
    COOLDOWN: int = 1
    TYPE = SkillType.OTHER
    ANIMATIONS: list[Animation] = [SLASH_ANIMATION, SLASH_ANIMATION, SLASH_ANIMATION]

# MANA VESSEL
class PurpleFlame(Skill):
    NAME: str = "purple flame"
    DESCRIPTION: str = "a burst of intense purple mana flames."
    MESSAGE: str = "{entity} unleashes purple flames on {target}!"
    BASE_DAMAGE: int = 14
    BASE_STUN: int = 1
    MN_COST: int = 8
    STARTUP: int = 9
    COOLDOWN: int = 2
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class ManaSiphon(Skill):
    NAME: str = "mana siphon"
    DESCRIPTION: str = "drains mana and super energy from the target."
    MESSAGE: str = "{entity} siphons energy from {target}!"
    BASE_DAMAGE: int = 4
    BASE_STUN: int = 1
    MN_COST: int = 0
    STARTUP: int = 6
    COOLDOWN: int = 3
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        drain = 10
        target.mn = max(0, target.mn - drain)
        entity.healMana(drain)
        if isinstance(target, Player):
             target.super = max(0, target.super - 10)
        if isinstance(entity, Player):
             entity.super = min(entity.max_super, entity.super + 10)
        printTypewriter(f"{Style.BRIGHT_BLUE}* siphoned 10 mana and 10 super!{Style.RESET}")

class CopySkill(Skill):
    NAME: str = "copy"
    DESCRIPTION: str = "copies the last skill used by the enemy to use as an art."
    MESSAGE: str = "{entity} mimics {target}'s resonance!"
    BASE_DAMAGE: int = 0
    BASE_STUN: int = 0
    MN_COST: int = 5
    STARTUP: int = 4
    COOLDOWN: int = 1
    TYPE = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
        if target.last_skill_used:
            copied = target.last_skill_used.skill
            printTypewriter(f"{Style.MAGENTA}* copied {copied.name}!{Style.RESET}")
            # Temporary logic: just use it right now
            copied.use(entity, target)
        else:
            printTypewriter(f"{Style.BRIGHT_BLACK}* target hasn't used a skill yet.{Style.RESET}")

class ManaWave(Skill):
    NAME: str = "mana wave"
    DESCRIPTION: str = "a wide pulse of mana that pushes the target back."
    MESSAGE: str = "{entity} sends a mana wave towards {target}!"
    BASE_DAMAGE: int = 12
    BASE_STUN: int = 2
    MN_COST: int = 15
    STARTUP: int = 10
    COOLDOWN: int = 4
    TYPE = SkillType.EXPLOSION
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION]

class EtherFlash(Skill):
    NAME: str = "ether flash"
    DESCRIPTION: str = "a blinding flash of mana that makes the user harder to hit."
    MESSAGE: str = "{entity} creates an ether flash!"
    BASE_DAMAGE: int = 4
    BASE_STUN: int = 1
    MN_COST: int = 10
    STARTUP: int = 5
    COOLDOWN: int = 5
    TYPE = SkillType.OTHER
    def afterUse(self, entity: Entity, target: Entity, used: Skill.Used) -> None:
         from .effect import StatEffect
         StatEffect.apply(entity, "agility_pct", 30, 3)
         printTypewriter(f"{Style.BRIGHT_BLUE}* agility increased by 30%!{Style.RESET}")

class VesselOverload(Skill):
    NAME: str = "super: vessel overload"
    DESCRIPTION: str = "unleashes the full capacity of the mana vessel in a massive burst."
    MESSAGE: str = "{entity} OVERLOADS their vessel against {target}!"
    BASE_DAMAGE: int = 65
    BASE_STUN: int = 0
    MN_COST: int = 0
    SUPER_COST: int = 100
    STARTUP: int = 15
    COOLDOWN: int = 1
    TYPE = SkillType.EXPLOSION
    ANIMATIONS: list[Animation] = [EXPLOSION_ANIMATION, EXPLOSION_ANIMATION]