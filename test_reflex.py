from skelebash.lib.entity import Player, Entity
from skelebash.lib.skill import QuickBlock, Punch, HeavySlash, SkillType
from skelebash.lib.skill import playOut
from skelebash.lib.style import Style

# Setup
player = Player()
enemy = Entity()
enemy.name = "Test Enemy"

print("--- Testing Super Meter ---")
player.dealDamage(10, enemy)
print(f"Player Super: {player.super}% (Expected: 10.0%)")
player.takeDamage(20, enemy)
print(f"Player Super: {player.super}% (Expected: 15.0%)")

print("\n--- Testing Quick Block vs Melee (Parry) ---")
# Punch is Melee by default
punch = Punch()
punch.startup = 6
qblock = QuickBlock() # Startup 4, window (4, 9)
enemy.stun = 0
playOut(player, qblock, enemy, punch)
print(f"Enemy Stun: {enemy.stun} (Expected: 2 for parry)")

print("\n--- Testing Block Break ---")
heavy = HeavySlash()
heavy.type = SkillType.HEAVY_MELEE
player.stun = 0
playOut(player, qblock, enemy, heavy)
print(f"Player Stun: {player.stun} (Expected: 1 for block break)")

print("\n--- Testing Burst Requirement ---")
from skelebash.lib.skill import Burst
burst = Burst()
player.super = 39
print("Using Burst with 39%...")
playOut(player, burst, enemy, punch)
print(f"Player Super: {player.super} (Expected: 39 - not used)")

player.super = 41
print("Using Burst with 41%...")
playOut(player, burst, enemy, punch)
print(f"Player Super: {player.super} (Expected: 1.0 - used)")
