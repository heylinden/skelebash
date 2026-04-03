from skelebash.lib.item import Item
from skelebash.lib.itembundle import ItemBundle
from skelebash.lib.itemstack import ItemStack
from skelebash.lib.skill import Skill
from skelebash.lib.skillset import Skillset
from skelebash.lib.goal import Goal
from skelebash.lib.entity import Entity
from skelebash.lib.animation import Animation, SLASH_ANIMATION
from skelebash.lib.util import public

@public
class VenomFang(Item):
    NAME: str = "venom fang"
    DESCRIPTION: str = "a sharp tooth from an ancient venom dragon. used to upgrade the venom dagger."
    USABLE: bool = False
    HAS_LEVELS: bool | int = False

@public
class VenomSlash(Skill):
    NAME: str = "venom slash"
    DESCRIPTION: str = "slash your enemy with poison."
    DAMAGE: int = 14
    STUN: int = 0
    CRIT_CHANCE_PCT: int = 25
    WHIFF_CHANCE_PCT: int = 25
    ST_COST: int = 15
    MN_COST: int = 0
    STARTUP: int = 15
    IFRAMES: bool = False
    HYPERARMOR: bool = False
    LOCKED: bool = False
    UNLOCK_AT_MASTERY: int = 0
    COOLDOWN: int = 1
    STARTING_COOLDOWN: int = 0
    ANIMATION: Animation | None = SLASH_ANIMATION

@public
class VenomDagger(Item):
    NAME: str = "venom dagger"
    DESCRIPTION: str = "a dagger with a green tint, capable of releasing deadly poison through its blade."
    RARITY: str = Item.Rarity.LEGENDARY
    USABLE: bool = True 
    USE_TEXT: str = "equip"
    HAS_LEVELS: bool = True
    HAS_MASTERY: bool = True
    UPGRADE_COSTS: list[ItemBundle] = [
        ItemBundle(
            VenomFang()*1,   # level 1 
        ),
        ItemBundle(
            VenomFang()*1,   # level 2 
        ),
        ItemBundle(
            VenomFang()*1,   # level 3 
        ),
        ItemBundle(
            VenomFang()*1,   # level 4 
        ),
        ItemBundle(
            VenomFang()*1,   # level 5 
        ),
        ItemBundle(
            VenomFang()*1,   # level 6 
        ),
        ItemBundle(
            VenomFang()*2,   # level 7 
        ),
        ItemBundle(
            VenomFang()*2,   # level 8 
        ),
        ItemBundle(
            VenomFang()*2,   # level 9 
        ),
        ItemBundle(
            VenomFang()*2,   # level 10 
        ),
        ItemBundle(
            VenomFang()*2,   # level 11 
        ),
        ItemBundle(
            VenomFang()*2,   # level 12 
        ),
        ItemBundle(
            VenomFang()*2,   # level 13 
        ),
        ItemBundle(
            VenomFang()*2,   # level 14 
        ),
        ItemBundle(
            VenomFang()*3,   # level 15 
        ),
        ItemBundle(
            VenomFang()*3,   # level 16 
        ),
        ItemBundle(
            VenomFang()*3,   # level 17 
        ),
        ItemBundle(
            VenomFang()*3,   # level 18 
        ),
        ItemBundle(
            VenomFang()*4,   # level 19 
        ),
        ItemBundle(
            VenomFang()*4,   # level 20 
        ),
        ItemBundle(
            VenomFang()*4,   # level 21 
        ),
        ItemBundle(
            VenomFang()*4,   # level 22 
        ),
        ItemBundle(
            VenomFang()*5,   # level 23 
        ),
        ItemBundle(
            VenomFang()*5,   # level 24 
        ),
        ItemBundle(
            VenomFang()*5,   # level 25 
        ),
        ItemBundle(
            VenomFang()*6,   # level 26 
        ),
        ItemBundle(
            VenomFang()*6,   # level 27 
        ),
        ItemBundle(
            VenomFang()*7,   # level 28 
        ),
        ItemBundle(
            VenomFang()*7,   # level 29 
        ),
        ItemBundle(
            VenomFang()*8,   # level 30 
        ),
    ]
    UPGRADE_BUFFS: list[list[str]] = [
        [],                                                          # level 1
        ["+2% damage"],                                              # level 2
        ["+4% damage"],                                              # level 3
        ["+6% damage"],                                              # level 4
        ["+8% damage"],                                              # level 5
        ["+10% damage", "+10% poison damage"],                       # level 6
        ["+12% damage", "+12% poison damage"],                       # level 7
        ["+14% damage", "+14% poison damage"],                       # level 8
        ["+16% damage", "+16% poison damage"],                       # level 9
        ["+18% damage", "+18% poison damage"],                       # level 10
        ["+20% damage", "+20% poison damage", "+5% crit chance"],    # level 11
        ["+22% damage", "+22% poison damage", "+6% crit chance"],    # level 12
        ["+24% damage", "+24% poison damage", "+7% crit chance"],    # level 13
        ["+26% damage", "+26% poison damage", "+8% crit chance"],    # level 14
        ["+28% damage", "+28% poison damage", "+9% crit chance"],    # level 15
        [
            "+30% damage", "+30% poison damage", "+10% crit chance",
            "poison stacks now last 1 turn longer"
        ],                                                          # level 16
        [
            "+32% damage", "+32% poison damage", "+11% crit chance",
            "poison stacks now last 1 turn longer"
        ],                                                          # level 17
        [
            "+34% damage", "+34% poison damage", "+12% crit chance",
            "poison stacks now last 1 turn longer"
        ],                                                          # level 18
        [
            "+36% damage", "+36% poison damage", "+13% crit chance",
            "poison stacks now last 1 turn longer"
        ],                                                          # level 19
        [
            "+38% damage", "+38% poison damage", "+14% crit chance",
            "poison stacks now last 1 turn longer"
        ],                                                          # level 20
        [
            "+40% damage", "+40% poison damage", "+15% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit"
        ],                                                          # level 21
        [
            "+42% damage", "+42% poison damage", "+16% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit"
        ],                                                          # level 22
        [
            "+44% damage", "+44% poison damage", "+17% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit"
        ],                                                          # level 23
        [
            "+46% damage", "+46% poison damage", "+18% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit"
        ],                                                          # level 24
        [
            "+48% damage", "+48% poison damage", "+19% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit"
        ],                                                          # level 25
        [
            "+50% damage", "+50% poison damage", "+20% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit",
            "+1 level poison"
        ],                                                          # level 26
        [
            "+52% damage", "+52% poison damage", "+22% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit",
            "+1 level poison"
        ],                                                          # level 27
        [
            "+54% damage", "+54% poison damage", "+24% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit",
            "+1 level poison"
        ],                                                          # level 28
        [
            "+56% damage", "+56% poison damage", "+26% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit",
            "+1 level poison"
        ],                                                          # level 29
        [
            "+60% damage", "+60% poison damage", "+30% crit chance",
            "poison stacks now last 1 turn longer",
            "inflict +1 level poison on crit",
            "+1 level poison",
            "deal venom effect instead of poison which bypasses i-frames"
        ],                                                          # level 30
    ]
    GOALS: list[Goal] = []
    SKILLSET: Skillset | None = Skillset(
        VenomSlash()
    )
    def onUse(self, entity: Entity) -> None:
        self.equipAsArmament(entity)