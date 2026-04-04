from skelebash.lib.brain import ComplexBrain
from skelebash.lib.entity import Entity
from skelebash.lib.skillset import Skillset
from skelebash.lib.skill import Punch

class MockEntity(Entity):
    def __init__(self, hp, max_hp):
        super().__init__()
        self.hp = hp
        self.max_hp = max_hp
        self.skills = Skillset(Punch())

def test_ai_reasoning():
    brain = ComplexBrain()
    player = MockEntity(100, 100)
    enemy = MockEntity(20, 100) # Low HP
    
    skill, reason = brain.decide(enemy, player)
    print(f"Action: {skill.name if skill else 'None'}")
    print(f"Reasoning: {reason}")
    print("-" * 20)
    
    enemy_high = MockEntity(100, 100)
    skill, reason = brain.decide(enemy_high, player)
    print(f"Action: {skill.name if skill else 'None'}")
    print(f"Reasoning: {reason}")

if __name__ == "__main__":
    test_ai_reasoning()
