from __future__ import annotations
import sys

from skelebash.lib.style import printTypewriter
from skelebash.lib.skelebash import Skelebash
from skelebash.mods.venom import VenomDagger, VenomFang
from skelebash.lib.item import IronChip
from skelebash.lib.skelepanel import skelepanel
from skelebash.lib.character import BASE_CHARACTER_LIST
from skelebash.mods.test import Slime


skelebash: Skelebash = Skelebash.promptLoad(BASE_CHARACTER_LIST, sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None, sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None)    


def main() -> None:
    if skelebash.new:
        from skelebash.lib.skill import Punch
        from skelebash.lib.entity import Entity
        
        skelebash.player.skills.skills.append(Punch())
        skelebash.player.inventory.add(VenomDagger()*1)
        skelebash.player.inventory.add(VenomFang()*30)
        skelebash.player.inventory.add(IronChip()*10)
        slime: Slime = Slime()
        skelebash.room.enemies = [slime]
        skelebash.saveGame()

    skelebash.startGame()
if "--skelepanel" in sys.argv:
    skelepanel(skelebash, main)
else:
    main()