import random
from typing import List, Dict
from generation.common.task_spec import TaskSpecification
import os

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
        # Read names from the file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        names_file = os.path.join(script_dir, 'dinner_party', 'names.txt')
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f]
        
        # Ensure we have enough names
        if len(names) < num_people:
            raise ValueError(f"Not enough names in the file. Need {num_people}, but only have {len(names)}.")
        
        # Randomly select unique names
        selected_names = random.sample(names, num_people)
        
        people = [Person.random_person(name, possible_interests) for name in selected_names]
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

if __name__ == "__main__":
    possible_interests = ["Music", "Art", "Sports", "Cooking", "Travel", "Literature", "Science", "Technology", "History", "Philosophy"]
    random_party = DinnerParty.random_dinner_party(num_people=10, possible_interests=possible_interests, set_size=5)
    print(random_party.to_prompt())
