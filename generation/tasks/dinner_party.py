import random
from typing import List, Dict
from generation.common.task_spec import TaskSpecification

class Person:
    def __init__(self, name: str, interests: Dict[str, int]):
        self.name = name
        self.interests = interests

    @classmethod
    def random_person(cls, name: str, possible_interests: List[str]):
        interests = {interest: random.randint(1, 5) for interest in random.sample(possible_interests, random.randint(1, len(possible_interests)))}
        return cls(name, interests)

class DinnerParty(TaskSpecification):
    def __init__(self, task_description: str, people: List[Person], set_size: int):
        super().__init__(task_description, [person.name for person in people], set_size)
        self.people = {person.name: person for person in people}

    def score_set(self, selected_set: List[str]) -> float:
        selected_people = [self.people[name] for name in selected_set]
        all_interests = {}
        for person in selected_people:
            for interest, level in person.interests.items():
                if interest not in all_interests:
                    all_interests[interest] = []
                all_interests[interest].append(level)
        
        top_3_interests = sorted(all_interests.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        return sum(sum(levels) for _, levels in top_3_interests)

    @classmethod
    def random_dinner_party(cls, num_people: int, possible_interests: List[str], set_size: int):
        people = [Person.random_person(f"Person_{i}", possible_interests) for i in range(num_people)]
        task_description = f"Select {set_size} people for a dinner party that will have the most engaging conversations."
        return cls(task_description, people, set_size)

    def to_prompt(self) -> str:
        """
        Generate a prompt string for the dinner party task.

        Returns:
        str: A string containing the task description, people and their interests, and the question.
        """
        prompt = f"{self.task_description}\n\nPeople and their interests:\n"
        for i, (name, person) in enumerate(self.people.items(), 1):
            interests_str = ", ".join([f"{interest} (level {level})" for interest, level in person.interests.items()])
            prompt += f"{i}. {name}: {interests_str}\n"
        prompt += f"\nPlease choose {self.set_size} people that would create the most engaging dinner party."
        return prompt
