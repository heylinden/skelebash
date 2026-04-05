from skelebash.lib.skill import Taunt
from skelebash.lib.entity import Player
from skelebash.lib.character import Balanced, Warrior, Ninja, Sorcerer
from skelebash.mod.test import Slime

Taunt().use(Warrior().ENTITY(), Slime())