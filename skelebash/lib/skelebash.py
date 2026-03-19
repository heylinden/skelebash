from __future__ import annotations
import random, pathlib, json, typing, gzip
try:
    import readline
except (ModuleNotFoundError, ImportError):
    ...

from .style import printStyle, Style, printCommandPrompt, clearScreen, enterToContinue, printTypewriter, prompt
from .entity import Player
from .constants import ADJECTIVES, LAST_OPENED_FILE, NOUNS, SAVES_DIR
from .util import deserialize, serialize
from .room import Room
from .dungeon import Dungeon, PlaceholderDungeon


class Skelebash:
    def __init__(self, player: Player | None = None, dungeon: Dungeon | None = None, save_id: str | None = None) -> None:
        self.player: Player = player or Player()
        self.dungeon: Dungeon = dungeon or PlaceholderDungeon()
        self.room: Room = self.dungeon.rooms[0].enter(self)
        self.new: bool = False
        self.temp: bool = False
        self.id: str = save_id or self.generateID()
        self.selected: typing.Any = self
    def __repr__(self) -> str:
        return f"Skelebash(\n  '{self.id}',\n  player={'\n'.join(['  '+line for line in repr(self.player).split('\n') if line.strip()]).strip()},\n  dungeon={'\n'.join(['  '+line for line in repr(self.dungeon).split('\n') if line.strip()]).strip()},\n  room={'\n'.join(['  '+line for line in repr(self.room).split('\n') if line.strip()]).strip()},\n  temp={self.temp}\n)"
    @classmethod
    def promptLoad(cls, choose: str | None = None) -> Skelebash:
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
            inp: str = (choose or prompt("load", self))
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
                    printTypewriter("welcome to skelebash! if this is your first time playing, you can refer to the help/tutorial document here: https://github.com/timespilot/skelebash/blob/master/HELP.md.", 0.01)
                    enterToContinue()
                clearScreen()
                skelebash: cls = cls()
                skelebash.new = True
                skelebash.saveGame()
                with LAST_OPENED_FILE.open("w") as file:
                    file.write(skelebash.id)
                return skelebash
            elif inp == "t":
                skelebash: cls = cls()
                skelebash.new = True
                skelebash.temp = True
                with LAST_OPENED_FILE.open("w") as file:
                    file.write(skelebash.id)
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
            
            # Print VS Layout
            printPanel(self.player.getInfoBar(), printer=(lambda t: printTypewriter(t, 0.005)) if first else printStyle)
            breakLine()
            printStyle(f"      {Style.BOLD}{Style.RED}VS{Style.RESET}")
            breakLine()
            
            for trait_or_effect in self.player.traits + self.player.effects:
                trait_or_effect.onTurnStart(self.player)

            for enemy in self.room.enemies:
                printPanel(enemy.getInfoBar(), printer=(lambda t: printTypewriter(t, 0.005)) if first else printStyle)
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
            printCommandPrompt("s", "skill tree", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("t", "traits", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("?", "help", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            if not self.temp:
                printCommandPrompt("sg", "save game", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            printCommandPrompt("q!", "quit without saving", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)
            if not self.temp:
                printCommandPrompt("sq", "save and quit", (lambda text: printTypewriter(text, 0.005) )if first else printStyle)

            first = False

            inp: str = prompt("", self)

            player_skill = None
            active_enemy = self.room.enemies[0]

            if inp == "a":
                printTypewriter("select category:")
                printCommandPrompt("1", "stance")
                printCommandPrompt("2", "art")
                printCommandPrompt("3", "armament")
                cat_inp = prompt("attack", self)
                
                selected_skillset: Stance | Art | Armament | None = {"1": self.player.stance, "2": self.player.art, "3": self.player.armament}.get(cat_inp)
                
                if not selected_skillset or not selected_skillset.skills:
                    printTypewriter("you have no skills in this category!")
                    enterToContinue()
                    continue
                
                # Check for available skills
                available_skills = [sk for sk in selected_skillset.skills if sk.active_cooldown == 0]
                if not available_skills:
                    printTypewriter("all skills in this category are on cooldown!")
                    enterToContinue()
                    continue

                printTypewriter("select skill:")
                for i, sk in enumerate(available_skills):
                    printCommandPrompt(str(i+1), f"{sk.name} ({sk.st_cost} ST, {sk.mn_cost} MN)")
                
                sk_inp = prompt("skill", self)
                if sk_inp.isdigit() and 1 <= int(sk_inp) <= len(available_skills):
                    player_skill = available_skills[int(sk_inp)-1]
                else:
                    continue
            elif inp == "p":
                printTypewriter("you pass your turn.")
                pass
            elif inp == "i":
                printTypewriter("\n--- inventory ---", 0.01)
                if not self.player.inventory.itemstacks:
                    printTypewriter(f"{Style.BRIGHT_BLACK}your inventory is empty.")
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
                while True:
                    clearScreen()
                    printTypewriter("\n--- SKILL TREE / ATTRIBUTES ---", 0.005)
                    printTypewriter(f"Available Skill Points: {Style.YELLOW}{self.player.skill_points}{Style.RESET}", 0.005)
                    printCommandPrompt("1", f"Upgrade Max HP (currently: {self.player.max_hp}) -> +10")
                    printCommandPrompt("2", f"Upgrade Max SP (currently: {self.player.max_st}) -> +10")
                    printCommandPrompt("3", f"Upgrade Max MN (currently: {self.player.max_mn}) -> +5")
                    printCommandPrompt("4", f"Upgrade Strength (currently: {self.player.strength_pct}%) -> +5%")
                    printCommandPrompt("5", f"Upgrade Defense (currently: {self.player.defense_pct}%) -> +5%")
                    printCommandPrompt("b", "back")
                    
                    s_inp = prompt("upgrade", self)
                    if s_inp == "b":
                        break
                    
                    if self.player.skill_points <= 0:
                        printTypewriter(f"{Style.RED}Not enough skill points!{Style.RESET}")
                        enterToContinue()
                        continue
                        
                    if s_inp == "1":
                        self.player.max_hp += 10
                        self.player.hp += 10
                    elif s_inp == "2":
                        self.player.max_st += 10
                        self.player.st += 10
                    elif s_inp == "3":
                        self.player.max_mn += 5
                        self.player.mn += 5
                    elif s_inp == "4":
                        self.player.strength_pct += 5
                    elif s_inp == "5":
                        self.player.defense_pct += 5
                    else:
                        continue
                        
                    self.player.skill_points -= 1
                    printTypewriter(f"{Style.BRIGHT_GREEN}Attribute upgraded!{Style.RESET}")
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

            if not active_enemy.brain:
                from .brain import ComplexBrain
                active_enemy.brain = ComplexBrain()
            
            printTypewriter(f"\n--- {active_enemy.name + ('\'' if active_enemy.name.endswith('s') else '\'s')} turn ---")
            printTypewriter(f"\n{Style.BRIGHT_BLACK}thinking...\n", 0.1)

            enemy_skill = active_enemy.brain.decide(active_enemy, self.player)

            success = playOut(self.player, player_skill, active_enemy, enemy_skill)
            
            enterToContinue()
            if success:
                self.tick()
    def tick(self) -> None:
        for attribute in self.__dict__:
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