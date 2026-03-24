from __future__ import annotations
import typing
import random


class Brain:
    def decide(self, entity: Entity, target: Entity) -> Skill | None:
        """Returns the skill the entity wants to use, or None to pass the turn."""
        return None
    def onTick(self, entity: Entity, target: Entity) -> None:
        pass

class RandomBrain(Brain):
    def decide(self, entity: Entity, target: Entity) -> Skill | None:
        if entity.skills and entity.skills.skills:
            available_skills = [sk for sk in entity.skills.skills if sk.active_cooldown == 0]
            if available_skills:
                return random.choice(available_skills)
        return None

class ComplexBrain(Brain):
    def decide(self, entity: Entity, target: Entity) -> Skill | None:
        available_skills = []
        if entity.skills and entity.skills.skills:
            available_skills.extend(entity.skills.skills)

        available_skills = [sk for sk in available_skills if sk.active_cooldown == 0]
        if not available_skills:
            return None

        # Prioritize block if HP < 30%
        hp_pct = entity.hp / entity.max_hp if entity.max_hp > 0 else 0
        if hp_pct < 0.3:
            defensive_skills = [sk for sk in available_skills if "block" in sk.name.lower() or "guard" in sk.name.lower()]
            if defensive_skills:
                return random.choice(defensive_skills)

        # Otherwise pick highest damage skill
        offensive_skills = sorted(available_skills, key=lambda sk: sk.base_damage, reverse=True)
        if offensive_skills:
            # 70% chance to use best skill, 30% chance for random to vary behaviour
            if random.random() < 0.7:
                return offensive_skills[0]
            return random.choice(available_skills)
        
        return None