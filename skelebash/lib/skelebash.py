from __future__ import annotations
import random, pathlib, json, typing, gzip
try:
    import readline
except (ModuleNotFoundError, ImportError):
    pass

from .style import printStyle, Style, printCommandPrompt, clearScreen, enterToContinue, printTypewriter, prompt, printCentered
from .entity import Player
from .effect import ArtAmplifiedEffect
from .constants import ADJECTIVES, LAST_OPENED_FILE, NOUNS, SAVES_DIR
from .util import deserialize, serialize
from .room import Room
from .dungeon import Dungeon, PlaceholderDungeon
from .character import Character, Balanced, chooseCharacter


class Skelebash:
    def __init__(self, player: Player | None = None, player_character: Character | None = None, dungeon: Dungeon | None = None, save_id: str | None = None) -> None:
        self.player: Player = player or Player()
        self.player_character: Character = player_character or Balanced()
        self.dungeon: Dungeon = dungeon or PlaceholderDungeon()
        self.room: Room = self.dungeon.rooms[0].enter(self)
        self.new: bool = False
        self.temp: bool = False
        self.id: str = save_id or self.generateID()
        self.selected: typing.Any = self
    def __repr__(self) -> str:
        player_repr: str = '\n'.join(['  '+line for line in repr(self.player).split('\n') if line.strip()]).strip()
        dungeon_repr: str = '\n'.join(['  '+line for line in repr(self.dungeon).split('\n') if line.strip()]).strip()
        room_repr: str = '\n'.join(['  '+line for line in repr(self.room).split('\n') if line.strip()]).strip()
        return f"Skelebash(\n  '{self.id}',\n  player={player_repr},\n  dungeon={dungeon_repr},\n  room={room_repr},\n  temp={self.temp}\n)"
    @classmethod
    def promptLoad(cls, chars: list[Character], choose: str | None = None, choose_char: str | None = None) -> Skelebash:
        if not choose:
            printTypewriter("pick or create a save:")
        d: dict[str, dict] = {}
        saves: list[tuple[pathlib.Path, dict]] = []
        for path in [child for child in list(SAVES_DIR.iterdir()) if child.name.endswith(".save")]:
            path = pathlib.Path(path)
            with gzip.open(path, "rt", encoding="utf-8") as file:
                content: str = file.read()
            if not content:
                path.unlink()
                continue
            saves.append((path, json.loads(content)))
        with LAST_OPENED_FILE.open() as file:
            last_opened: str = file.read()
        for i, (path, save) in enumerate(saves, start=1):
            name: str = path.name.removesuffix('.save')
            if not choose:
                printCommandPrompt(str(i), f"{name}{' | '+Style.BOLD+'last opened'+Style.RESET if last_opened == name else ''}")
            d[str(i)] = save
        if not choose:
            printCommandPrompt("n", "new save")
            printCommandPrompt("t", "temporary test run (cannot save!)")
        while True:
            inp: str = (choose or prompt("load", safe=True))
            if inp in d:
                skelebash: cls = deserialize(d[inp])
                skelebash.new = False
                skelebash.saveGame()
                if not choose:
                    printTypewriter(f"loading save: {skelebash.id} ({inp})...", 0.01)
                    enterToContinue()
                clearScreen()
                with LAST_OPENED_FILE.open("w") as file:
                    file.write(skelebash.id)
                return skelebash
            elif inp == "n":
                if not choose:
                    printTypewriter("welcome to skelebash! if this is your first time playing, you can refer to the help/tutorial document here: https://github.com/heylinden/skelebash/blob/master/HELP.md.", 0.01)
                    enterToContinue()
                clearScreen()
                skelebash: cls = cls()
                skelebash.new = True
                skelebash.saveGame()
                with LAST_OPENED_FILE.open("w") as file:
                    file.write(skelebash.id)
                character: Character | None = chooseCharacter(chars, choose_char)
                if not character:
                    exit(0)
                skelebash.player_character = character
                skelebash.player = character.entity()
                return skelebash
            elif inp == "t":
                skelebash: cls = cls()
                skelebash.new = True
                skelebash.temp = True
                with LAST_OPENED_FILE.open("w") as file:
                    file.write(skelebash.id)
                character: Character | None = chooseCharacter(chars, choose_char)
                if not character:
                    exit(0)
                skelebash.player_character = character
                skelebash.player = character.entity()
                if not choose:
                    printTypewriter(f"loaded temporary test run", 0.01)
                    enterToContinue()
                clearScreen()
                return skelebash
            elif not inp:
                continue
            else:
                printTypewriter(f"{Style.RED}invalid input")
                if choose:
                    exit(1)
    
    def startGame(self) -> None:
        from .skill import playOut
        from .style import clearScreen, printPanel, printCentered, breakLine

        first: bool = True
        turn_n: int = 0
        while True:
            turn_n += 1
            clearScreen()
            
            printPanel(self.player.getInfoBar(), printer=printCentered)
            breakLine()
            printCentered(f"{Style.BOLD}{Style.RED}--- VS ---{Style.RESET}")
            breakLine()
            
            for trait_or_effect in self.player.traits + self.player.effects:
                trait_or_effect.onTurnStart(self.player)

            for i, enemy in enumerate(self.room.enemies):
                printPanel(enemy.getInfoBar(fighting=i == 0), printer=printCentered)
                breakLine()

            if self.player.hp <= 0:
                self.player.die()
                printTypewriter(f"{Style.BRIGHT_RED}you passed away... game over.{Style.RESET}")
                enterToContinue()
                break

            self.room.enemies = [e for e in self.room.enemies if e.hp > 0]
            if not self.room.enemies:
                printTypewriter(f"\n{Style.BRIGHT_GREEN}room cleared!{Style.RESET}")
                enterToContinue()
                break

            ((lambda text: printTypewriter(text, 0.01) )if first else printStyle)(f"\n{Style.BOLD}--- your turn ---{Style.RESET}")
            printCommandPrompt("a", "attack", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("p", "pass", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("i", "inventory", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("e", "effects", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("s", "skill tree/attributes", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("t", "traits", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("?", "help", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            if not self.temp:
                printCommandPrompt("sg", "save game", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("q!", "quit without saving", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            if not self.temp:
                printCommandPrompt("sq", "save and quit", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)

            breakLine()

            first = False
            if not self.player.stun:
                inp: str = prompt("", self)
            else:
                printTypewriter(f"* {self.player.name} is stunned!")
                inp = "p"

            player_skill = None
            active_enemy = self.room.enemies[0]

            if inp == "a":
                printTypewriter("select category:")
                printCommandPrompt("1", f"{Style.BRIGHT_BLACK if not self.player.stance.skills else ''}stance {'['+self.player.stance.name+']' if self.player.stance.name else ''} ({len(self.player.stance.skills)} skill{'' if len(self.player.stance.skills) == 1 else 's'}){Style.RESET}")
                printCommandPrompt("2", f"{Style.BRIGHT_BLACK if not self.player.art.skills else ''}art {'['+self.player.art.name+']' if self.player.art.name else ''} ({len(self.player.art.skills)} skill{'' if len(self.player.art.skills) == 1 else 's'}){Style.RESET}")
                printCommandPrompt("3", f"{Style.BRIGHT_BLACK if not self.player.armament.skills else ''}armament {'['+self.player.armament.name+']' if self.player.armament.name else ''} ({len(self.player.armament.skills)} skill{'' if len(self.player.armament.skills) == 1 else 's'}){Style.RESET}")
                printCommandPrompt("4", f"{Style.BRIGHT_BLACK if not self.player.follow_up.skills else ''}follow-up {'['+self.player.follow_up.name+']' if self.player.follow_up.name else ''} ({len(self.player.follow_up.skills)} skill{'' if len(self.player.follow_up.skills) == 1 else 's'}){Style.RESET}")
                printCommandPrompt("5", f"{Style.BRIGHT_BLACK if not self.player.reflex.skills else ''}reflex {'['+self.player.reflex.name+']' if self.player.reflex.name else ''} ({len(self.player.reflex.skills)} skill{'' if len(self.player.reflex.skills) == 1 else 's'}){Style.RESET}")
                printCommandPrompt("b", "back")
                while True:
                    cat_inp = prompt("attack", self)
                    if cat_inp:
                        break
                if cat_inp == "b":
                    continue
                
                selected_skillset: Stance | Art | Armament | Reflex | FollowUp | None = {"1": self.player.stance, "2": self.player.art, "3": self.player.armament, "4": self.player.follow_up, "5": self.player.reflex}.get(cat_inp)
                
                if not selected_skillset:
                    printTypewriter("that category does not exist.")
                    enterToContinue()
                    continue
                if not selected_skillset.skills:
                    printTypewriter("you have no skills in this category!")
                    enterToContinue()
                    continue

                printTypewriter("select skill:")
                for i, skill in enumerate(selected_skillset.skills):
                    printCommandPrompt(str(i+1), f"{Style.REDDISH_PINK if skill.super_cost == 100 else ''}{Style.BRIGHT_BLACK if skill.active_cooldown else ''}{skill.name} {Style.BRIGHT_BLACK}[{skill.startup}f]{Style.RESET} ({skill.st_cost}st, {skill.mn_cost}mn{(', '+str(skill.super_cost)+'sp') if skill.super_cost else ''})" + (f"{Style.BRIGHT_BLACK} | {skill.active_cooldown} turn{'' if skill.active_cooldown == 1 else 's'}{Style.RESET}" if skill.active_cooldown else ""))
                printCommandPrompt("b", "back")

                while True:
                    sk_inp = prompt("skill", self)
                    if sk_inp:
                        break
                if sk_inp == "b":
                    continue
                if sk_inp.isdigit() and 1 <= int(sk_inp) <= len(selected_skillset.skills):
                    skill: Skill = selected_skillset.skills[int(sk_inp)-1]
                    st_cost = skill.st_cost
                    mn_cost = skill.mn_cost
                    super_cost = skill.super_cost
                    for effect in self.player.effects:
                        if isinstance(effect, ArtAmplifiedEffect) and effect.boost_type in ["stamina", "ultimate", "all"]:
                            if any(isinstance(s, self.__class__) for s in entity.art.skills):
                                st_cost = 0
                                printTypewriter(f"{Style.BRIGHT_GREEN}* stamina cost reduced to 0 by focus!{Style.RESET}")
                                break
                    if self.player.super < super_cost:
                        printTypewriter(f"{Style.RED}* not enough super. ({self.player.super} / {super_cost})")
                        enterToContinue()
                        continue
                    if self.player.st < st_cost:
                        printTypewriter(f"{Style.RED}* not enough stamina. ({self.player.st} / {st_cost})")
                        enterToContinue()
                        continue
                    if self.player.mn < mn_cost:
                        printTypewriter(f"{Style.RED}* not enough mana. ({self.player.mn} / {mn_cost})")
                        enterToContinue()
                        continue
                    self.player.st -= st_cost
                    self.player.mn -= mn_cost
                    if skill.active_cooldown:
                        printTypewriter(f"{Style.BRIGHT_BLACK}* skill is on cooldown for {skill.active_cooldown} more turns.{Style.RESET}")
                        enterToContinue()
                        continue
                    player_skill = skill
                else:
                    continue
            elif inp == "p":
                pass
            elif inp == "i":
                printTypewriter("\n--- inventory ---", 0.01)
                if not self.player.inventory.itemstacks:
                    printTypewriter(f"{Style.BRIGHT_BLACK}* your inventory is empty.")
                    enterToContinue()
                    continue
                for i, stack in enumerate(self.player.inventory.itemstacks):
                    printCommandPrompt(str(i+1), f"{stack.count}x {stack.item.name}")
                printCommandPrompt("c", "cancel")
                i_inp: str = prompt("inventory", self)
                if i_inp.isdigit() and 1 <= int(i_inp) <= len(self.player.inventory.itemstacks):
                    self.player.inventory.itemstacks[int(i_inp)-1].item.showInfo(self.player, self)
                elif i_inp == "c" or not i_inp:
                    continue
                else:
                    printTypewriter(f"{Style.RED}invalid input")
                    enterToContinue()
                continue
            elif inp == "e":
                printTypewriter("\n--- effects ---", 0.01)
                if not self.player.effects:
                    printTypewriter(f"{Style.BRIGHT_BLACK}you have no active effects.")
                else:
                    for effect in self.player.effects:
                        printTypewriter(f"  [{effect.name}] duration: {effect.duration} turns")
                enterToContinue()
                continue
            elif inp == "t":
                printTypewriter("\n--- traits ---", 0.01)
                if not self.player.traits:
                    printTypewriter(f"{Style.BRIGHT_BLACK}you have no traits.")
                else:
                    for trait in self.player.traits:
                        printTypewriter(f"  [{trait.name}] {trait.description}")
                enterToContinue()
                continue
            elif inp == "s":
                skill_tree_first: bool = True
                while True:
                    clearScreen()
                    ((lambda s: printTypewriter(s, 0.005)) if skill_tree_first else printStyle)("\n--- skill tree / attributes ---")
                    ((lambda s: printTypewriter(s, 0.005)) if skill_tree_first else printStyle)(f"* available skill points: {Style.YELLOW}{self.player.skill_points}{Style.RESET}")
                    printCommandPrompt("1", f"{Style.BRIGHT_RED}upgrade max hp (hit points/health):                          {self.player.max_hp}hp -> {self.player.max_hp+2}hp", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("2", f"{Style.YELLOW}upgrade max st (stamina):                                    {self.player.max_st}st -> {self.player.max_st+2}st", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("3", f"{Style.YELLOW}upgrade st recovery:                                         {self.player.st_recovery}st/turn -> {self.player.st_recovery+1}st/turn", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("4", f"{Style.BRIGHT_BLUE}upgrade max mn (mana):                                       {self.player.max_mn}mn -> {self.player.max_mn+2}mn", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)   
                    printCommandPrompt("5", f"{Style.BRIGHT_BLUE}upgrade mn recovery:                                         {self.player.mn_recovery}mn/turn -> {self.player.mn_recovery+1}mn/turn", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("6", f"{Style.BRIGHT_GREEN}upgrade max bh (block health):                               {self.player.max_bh}bh -> {self.player.max_bh+2}bh", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("7", f"{Style.BRIGHT_GREEN}upgrade bh recovery:                                         {self.player.bh_recovery}bh/turn -> {self.player.bh_recovery+1}bh/turn", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("8", f"{Style.RED}upgrade strength (dealt damage increase):                    {self.player.strength_pct}% -> {self.player.strength_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("9", f"{Style.BLUE}upgrade defense (taken damage reduction):                    {self.player.defense_pct}% -> {self.player.defense_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("10", f"{Style.GREEN}upgrade precision (dealt crit chance increase):             {self.player.precision_pct}% -> {self.player.precision_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("11", f"{Style.YELLOW}upgrade force (dealt crit damage increase):                 {self.player.force_pct}% -> {self.player.force_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("12", f"{Style.MAGENTA}upgrade concentration (dealt whiff chance reduction):       {self.player.concentration_pct}% -> {self.player.concentration_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("13", f"{Style.ORANGE}upgrade agility (taken whiff chance increase):              {self.player.agility_pct}% -> {self.player.agility_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("14", f"{Style.BRIGHT_BLACK}upgrade durability (taken crit chance reduction):           {self.player.durability_pct}% -> {self.player.durability_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("15", f"{Style.BRIGHT_GREEN}upgrade block strength (outgoing block damage increase):    {self.player.block_strength_pct}% -> {self.player.block_strength_pct+10}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("17", f"{Style.BRIGHT_GREEN}upgrade block efficiency (incoming block damage reduction): {self.player.block_efficiency_pct}% -> {self.player.block_efficiency_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("18", f"{Style.BRIGHT_BLUE}upgrade hyperarmor strength (outgoing hyperarmor increase): {self.player.hyperarmor_strength_pct}% -> {self.player.hyperarmor_strength_pct+10}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("19", f"{Style.BRIGHT_BLUE}upgrade hyperarmor defense (incoming hyperarmor reduction): {self.player.hyperarmor_defense_pct}% -> {self.player.hyperarmor_defense_pct+5}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    printCommandPrompt("20", f"{Style.REDDISH_PINK}upgrade super gain: {self.player.super_gain_pct}% -> {self.player.super_gain_pct+10}%", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)                    
                    printCommandPrompt("b", "back", (lambda s: printTypewriter(s, 0.0001)) if skill_tree_first else printStyle)
                    
                    skill_tree_first = False

                    s_inp = prompt("upgrade", self)
                    if s_inp == "b":
                        break
                    
                    if self.player.skill_points <= 0:
                        printTypewriter(f"{Style.RED}* not enough skill points!{Style.RESET}")
                        enterToContinue()
                        continue
                        
                    match s_inp:
                        case "1":
                            self.player.max_hp += 2
                        case "2":
                            self.player.hp_recovery += 1
                        case "3":
                            self.player.max_st += 2
                        case "4":
                            self.player.st_recovery += 1
                        case "5":
                            self.player.max_mn += 2
                        case "6":
                            self.player.mn_recovery += 1
                        case "7":
                            self.player.max_bh += 2
                        case "8":
                            self.player.bh_recovery += 1
                        case "9":
                            self.player.strength_pct += 5
                        case "10":
                            self.player.defense_pct += 5
                        case "11":
                            self.player.precision_pct += 5
                        case "12":
                            self.player.force_pct += 5
                        case "13":
                            self.player.concentration_pct += 5
                        case "14":
                            self.player.agility_pct += 5
                        case "15":
                            self.player.durability_pct += 5
                        case "16":
                            self.player.block_strength_pct += 10
                        case "17":
                            self.player.block_efficiency_pct += 5
                        case "18":
                            self.player.hyperarmor_strength_pct += 10
                        case "19":
                            self.player.hyperarmor_defense_pct += 5
                        case "20":
                            self.player.super_gain_pct += 10
                        case _:
                            continue
                        
                    self.player.skill_points -= 1
                    printTypewriter(f"{Style.BRIGHT_GREEN}* attribute upgraded!{Style.RESET}")
                    enterToContinue()
                continue
            elif inp == "?":
                printTypewriter(
                    f"use the {Style.BOLD}[a]{Style.RESET} command ",
                    0.005
                )
                enterToContinue()
                continue
            elif inp == "sg" and not self.temp:
                self.saveGame()
                printTypewriter(f"{Style.BRIGHT_GREEN}game saved to {self.id}.save")
                enterToContinue()
                continue
            elif inp == "q!":
                exit(0)
            elif inp == "sq" and not self.temp:
                self.saveGame()
                printTypewriter(f"{Style.BRIGHT_GREEN}game saved to {self.id}.save")
                exit(0)
            elif not inp:
                continue
            else:
                printTypewriter(f"{Style.RED}invalid input")
                enterToContinue()
                continue
            enemy_skill: Skill | None = None
            if not active_enemy.stun:
                if not active_enemy.brain:
                    from .brain import ComplexBrain
                    active_enemy.brain = ComplexBrain()
                possessive: str = '\'' if active_enemy.name.endswith('s') else '\'s'
                printTypewriter(f"\n--- {active_enemy.name + possessive} turn ---")
                printTypewriter(f"\n{Style.BRIGHT_BLACK}thinking...\n", 0.05)
                enemy_skill, reasoning = active_enemy.brain.decide(active_enemy, self.player)
                if reasoning:
                    printTypewriter(f"{Style.BRIGHT_BLACK}{reasoning}{Style.RESET}", 0.03)
                    breakLine()
            else:
                printTypewriter(f"{active_enemy.name} is stunned!")

            success = playOut(self.player, player_skill, active_enemy, enemy_skill)
            
            enterToContinue()
            if success:
                print("tick!")
                self.onTick()
    def onTick(self) -> None:
        for key, attribute in self.__dict__.items():
            if key == "selected":
                continue
            if hasattr(attribute, "onTick"):
                attribute.onTick(self)
    def generateID(self) -> str:
        while True:
            save_id: str = f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}-{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
            if not (SAVES_DIR / f"{save_id}.save").exists():
                return save_id
    def select(self, obj: typing.Any) -> typing.Any:
        self.selected = obj
        return obj
    def saveGame(self) -> None:
        if self.temp:
            return
        with gzip.open(SAVES_DIR / f"{self.id}.save", "wt", encoding="utf-8") as file:
            json.dump(serialize(self), file, indent=4) # type: ignore