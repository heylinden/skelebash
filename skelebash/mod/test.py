from skelebash.lib.entity import Entity
from skelebash.lib.skillset import Skillset
from skelebash.lib.itembundle import ItemBundle
from skelebash.lib.skill import Punch


class Slime(Entity):
    NAME = "slime"
    HP = 30
    MAX_HP = 30
    SKILLS = Skillset(Punch())
    INVENTORY = ItemBundle()