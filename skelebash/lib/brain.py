from __future__ import annotations
import typing
import random


class Brain:
    def decide(self, entity: Entity, target: Entity) -> tuple[Skill | None, str | None]:
        """Returns a tuple of (skill, reasoning)."""
        return None, None
    def onTick(self, entity: Entity, target: Entity) -> None:
        pass

class RandomBrain(Brain):
    def decide(self, entity: Entity, target: Entity) -> tuple[Skill | None, str | None]:
        if entity.skills and entity.skills.skills:
            available_skills = [sk for sk in entity.skills.skills if sk.active_cooldown == 0]
            if available_skills:
                skill = random.choice(available_skills)
                return skill, f"choosing {skill.name} at random."
        return None, "no skills available, passing."

class ComplexBrain(Brain):
    def decide(self, entity: Entity, target: Entity) -> tuple[Skill | None, str | None]:
        available_skills = []
        if entity.skills and entity.skills.skills:
            available_skills.extend(entity.skills.skills)
        available_skills = [skill for skill in available_skills if skill.active_cooldown == 0]
        if not available_skills:
            return None, random.choice([
                "no offensive options found, passing.",
                "i'm out of options, i must pass.",
                "guess i'll just... pass.",
                "what am i supposed to do? i have no skills available.",
                "this pass will pay off in the future!",
                "just wait until my skills are off cooldown..."
            ])

        hp_pct = entity.hp / entity.calculate("max_hp") if entity.calculate("max_hp") > 0 else 0
        if hp_pct < 0.3:
            defensive_skills = [skill for skill in available_skills if "block" in skill.name.lower() or "guard" in skill.name.lower()]
            if defensive_skills:
                skill = random.choice(defensive_skills)
                return skill, f"my health is low ({round(hp_pct * 100)}%), focusing on defense with {skill.name}."

        offensive_skills = sorted(available_skills, key=lambda skill: skill.base_damage, reverse=True)
        if offensive_skills:
            if random.random() < 0.7:
                skill = offensive_skills[0]
                return skill, random.choice([
                    f"using {skill.name} as it's my strongest available move.",
                    f"i think {skill.name} is my best option.",
                    f"hah! {skill.name}!",
                    f"{skill.name} it is."
                ] + ([f"try interrupting my {skill.name}! bet you can't."]*5 if skill.iframes or skill.hyperarmor else [f"please don't interrupt my {skill.name}..."]))
            skill = random.choice(available_skills)
            return skill, random.choice([
                f"opting for {skill.name} to keep the pressure on.",
                f"bet you didn't think i'd use {skill.name}, hm?",
                f"i'll use {skill.name}.",
                f"why not a cheeky {skill.name}?",
                f"i'll use {skill.name} to try to interrupt you."
            ])
        
        return None, random.choice([
            "no offensive options found, passing.",
            "i'm out of options, i must pass.",
            "guess i'll just... pass.",
            "what am i supposed to do? i have no skills available.",
            "this pass will pay off in the future!",
            "just wait until my skills are off cooldown..."
        ])