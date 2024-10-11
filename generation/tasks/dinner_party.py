import random
from typing import List, Dict
from generation.common.task_spec import TaskSpecification
import os

class Person:
    def __init__(self, name: str, interests: Dict[str, int]):
        """
        Initialize a Person object.

        Args:
        name (str): The name of the person.
        interests (Dict[str, int]): A dictionary of interests and their levels.
        """
        self.name = name
        self.interests = interests

    @classmethod
    def random_person(cls, name: str, possible_interests: List[str]):
        """
        Create a random Person object with random interests.

        Args:
        name (str): The name of the person.
        possible_interests (List[str]): A list of possible interests to choose from.

        Returns:
        Person: A new Person object with randomly selected interests and levels.
        """
        interests = {interest: random.randint(1, 5) for interest in random.sample(possible_interests, random.randint(1, len(possible_interests)))}
        return cls(name, interests)

class DinnerParty(TaskSpecification):
    def __init__(self, task_description: str, people: List[Person], set_size: int):
        """
        Initialize a DinnerParty object.

        Args:
        task_description (str): The description of the dinner party task.
        people (List[Person]): A list of Person objects representing potential dinner party attendees.
        set_size (int): The number of people to be selected for the dinner party.
        """
        super().__init__(task_description, [person.name for person in people], set_size)
        self.people = {person.name: person for person in people}

    def score_set(self, selected_set: List[str], debug: bool = False) -> float:
        """
        Score a selected set of people for the dinner party.

        Args:
        selected_set (List[str]): A list of names of selected people.
        debug (bool): If True, print debug information about the scoring process.

        Returns:
        float: The score for the selected set of people.
        """
        selected_people = [self.people[name] for name in selected_set]
        all_interests = {}
        for person in selected_people:
            for interest, level in person.interests.items():
                if interest not in all_interests:
                    all_interests[interest] = []
                all_interests[interest].append(level)
        
        # Sort interests by count (descending), then by sum of levels (descending), then alphabetically
        sorted_interests = sorted(
            all_interests.items(),
            key=lambda x: (-len(x[1]), -sum(x[1]), x[0])
        )
        top_3_interests = sorted_interests[:3]
        score = sum(sum(levels) for _, levels in top_3_interests)

        if debug:
            print(f"Debug information for set: {selected_set}")
            print("Interest breakdown:")
            for interest, levels in all_interests.items():
                print(f"  {interest}: {levels} (count: {len(levels)}, sum: {sum(levels)})")
            print("Top 3 interests:")
            for interest, levels in top_3_interests:
                print(f"  {interest}: {levels} (count: {len(levels)}, sum: {sum(levels)})")
            print(f"Total score: {score}")

        return score

    @classmethod
    def random_dinner_party(cls, num_people: int, num_interests: int, set_size: int):
        """
        Create a random DinnerParty object.

        Args:
        num_people (int): The number of people to generate for the dinner party.
        num_interests (int): The number of possible interests to choose from.
        set_size (int): The number of people to be selected for the dinner party.

        Returns:
        DinnerParty: A new DinnerParty object with randomly generated people and interests.

        Raises:
        ValueError: If there are not enough names or interests in the respective files.
        """
        # Read names from the file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        names_file = os.path.join(script_dir, 'dinner_party', 'names.txt')
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f]
        
        # Read interests from the file
        interests_file = os.path.join(script_dir, 'dinner_party', 'interests.txt')
        with open(interests_file, 'r') as f:
            all_interests = [line.strip() for line in f]
        
        # Ensure we have enough names and interests
        if len(names) < num_people:
            raise ValueError(f"Not enough names in the file. Need {num_people}, but only have {len(names)}.")
        if len(all_interests) < num_interests:
            raise ValueError(f"Not enough interests in the file. Need {num_interests}, but only have {len(all_interests)}.")
        
        # Randomly select unique names and interests
        selected_names = random.sample(names, num_people)
        selected_interests = random.sample(all_interests, num_interests)
        
        people = [Person.random_person(name, selected_interests) for name in selected_names]
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

    def get_random_set(self) -> List[str]:
        """
        Return a random set of people for the dinner party.

        Returns:
        List[str]: A list of randomly selected people's names.
        """
        return random.sample(list(self.people.keys()), self.set_size)

if __name__ == "__main__":
    random_party = DinnerParty.random_dinner_party(num_people=10, num_interests=8, set_size=5)
    print(random_party.to_prompt())
    
    print("\nRandom set samples:")
    for i in range(3):
        random_set = random_party.get_random_set()
        print(f"\nSample {i+1}: {random_set}")
        score = random_party.score_set(random_set, debug=True)
        print(f"Final Score: {score}\n")
