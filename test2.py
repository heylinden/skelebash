from __future__ import annotations
import sys

from skelebash.lib.style import printTypewriter
from skelebash.lib.skelebash import Skelebash
from skelebash.mods.venom import VenomDagger, VenomFang
from skelebash.lib.skelepanel import skelepanel


skelebash: Skelebash = Skelebash.promptLoad(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None)    

def main() -> None:
    if skelebash.new:
        print("hi")
        skelebash.player.inventory.add(VenomDagger()*1)
        skelebash.player.inventory.add(VenomFang()*30)
    while True:
        ...

if "--skelepanel" in sys.argv:
    skelepanel(skelebash, main)
else:
    main()