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
        available_skills = [skill for skill in available_skills if skill.active_cooldown == 0]
        if not available_skills:
            return None

        hp_pct = entity.hp / entity.max_hp if entity.max_hp > 0 else 0
        if hp_pct < 0.3:
            defensive_skills = [skill for skill in available_skills if "block" in skill.name.lower() or "guard" in skill.name.lower()]
            if defensive_skills:
                return random.choice(defensive_skills)

        offensive_skills = sorted(available_skills, key=lambda skill: skill.base_damage, reverse=True)
        if offensive_skills:
            if random.random() < 0.7:
                return offensive_skills[0]
            return random.choice(available_skills)
        
        return None