import os
import random
from dataclasses import dataclass, field
from typing import Dict, List

import scipy.stats as stats

from generation.common.task_spec import TaskSpecification


@dataclass
class Person:
    name: str
    interests: Dict[str, int]

    def __post_init__(self):
        # Remove any interests with a value of None
        self.interests = {k: v for k, v in self.interests.items() if v is not None}

    @classmethod
    def random_person(cls, name: str, possible_interests: List[str], total_points: int, min_interests: int, max_interests: int):
        """
        Create a random Person object with random interests and a specified total number of points.

        Args:
        name (str): The name of the person.
        possible_interests (List[str]): A list of possible interests to choose from.
        total_points (int): The total number of points to distribute among interests.
        min_interests (int): The minimum number of interests a person can have.
        max_interests (int): The maximum number of interests a person can have.

        Returns:
        Person: A new Person object with randomly selected interests and levels.
        """
        if total_points < 1:
            return cls(name, {})

        num_interests = random.randint(min_interests, min(max_interests, len(possible_interests), total_points))
        selected_interests = random.sample(possible_interests, num_interests)
        
        interests = {}
        remaining_points = total_points
        
        # Ensure each interest gets at least one point
        for interest in selected_interests:
            interests[interest] = 1
            remaining_points -= 1
        
        # Distribute remaining points randomly
        while remaining_points > 0:
            interest = random.choice(selected_interests)
            points = random.randint(1, min(remaining_points, 5))  # Cap individual additions to 5 points
            interests[interest] += points
            remaining_points -= points
        
        return cls(name, interests)


@dataclass
class DinnerParty(TaskSpecification):
    task_description: str
    people: List[Person]
    set_size: int
    options: List[str] = field(init=False)
    target_score: float = 0.0
    stored_scores: List[float] = field(default_factory=list)

    def __post_init__(self):
        super().__init__(self.task_description, [person.name for person in self.people], self.set_size)
        self.options = [person.name for person in self.people]
        self._calculate_target_score()

    def _calculate_target_score(self, num_samples: int = 1000, kth: int = 3) -> None:
        """
        Calculate the target score by sampling random parties.

        Args:
        num_samples (int): The number of random samples to generate.
        kth (int): The position of the score to set as the target (e.g., 3 for the 3rd highest score).
        """
        self.stored_scores = []
        for _ in range(num_samples):
            random_set = self.get_random_set()
            score = self.score_set(random_set)
            self.stored_scores.append(score)
        self.stored_scores.sort(reverse=True)
        self.target_score = self.stored_scores[kth - 1] if kth <= len(self.stored_scores) else min(self.stored_scores)

    def get_score_statistics(self, score: float) -> Dict[str, float]:
        """
        Get the percentile ranking, absolute ranking, and percent of max score for a given score within the stored scores.

        Args:
        score (float): The score to rank.

        Returns:
        Dict[str, float]: A dictionary containing:
            - 'percentile': The percentile ranking of the score (0.0 to 1.0)
            - 'ranking': The absolute ranking of the score (1 being the highest)
            - 'percent_of_max': The percent of the maximum known score (0.0 to 1.0)
        """
        if not self.stored_scores:
            raise ValueError("No stored scores to compare against.")

        percentile = sum(1 for s in self.stored_scores if s <= score) / len(self.stored_scores)
        ranking = sum(1 for s in self.stored_scores if s > score) + 1
        max_score = max(self.stored_scores)
        percent_of_max = score / max_score if max_score > 0 else 1.0
        
        # Calculate normalized score using mean of stored scores
        avg_score = sum(self.stored_scores) / len(self.stored_scores)
        normalized_score = score / avg_score if avg_score > 0 else 1.0
        
        # Calculate rank normalized score using gaussian normalization
        # Add small offset to avoid exact 0 or 1 percentiles
        rank_percentile = (len(self.stored_scores) - ranking + 0.5) / (len(self.stored_scores) + 1.0)
        rank_normalized_score = stats.norm.ppf(rank_percentile)
        
        return {
            'percentile': percentile,
            'ranking': ranking,
            'percent_of_max': percent_of_max,
            'normalized_score': normalized_score,
            'rank_normalized_score': rank_normalized_score
        }

    def score_set(self, selected_set: List[str], debug: bool = False) -> float:
        """
        Score a selected set of people for the dinner party.

        Args:
        selected_set (List[str]): A list of names of selected people.
        debug (bool): If True, print debug information about the scoring process.

        Returns:
        float: The score for the selected set of people.
        """
        selected_people = [person for person in self.people if person.name in selected_set]
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
        
        # Calculate base score from top 3 interests
        top_3_interests = sorted_interests[:3]
        base_score = sum(sum(levels) for _, levels in top_3_interests)

        # Calculate final score
        score = base_score

        if debug:
            print(f"Debug information for set: {selected_set}")
            print("Interest breakdown:")
            for interest, levels in all_interests.items():
                print(f"  {interest}: {levels} (count: {len(levels)}, sum: {sum(levels)})")
            print("Top 3 interests:")
            for interest, levels in top_3_interests:
                print(f"  {interest}: {levels} (count: {len(levels)}, sum: {sum(levels)})")
            print(f"Base score: {base_score}")
            print(f"Total score: {score}")

        return score

    @classmethod
    def random_dinner_party(cls, num_people: int, num_interests: int, set_size: int, total_points: int, points_spread: int, min_interests: int, max_interests: int, bimodal_discount: int = 0):
        """
        Create a random DinnerParty object.

        Args:
        num_people (int): The number of people to generate for the dinner party.
        num_interests (int): The number of possible interests to choose from.
        set_size (int): The number of people to be selected for the dinner party.
        total_points (int): The total number of interest points to distribute among all people.
        points_spread (int): The plus or minus on a person's total point value.
        min_interests (int): The minimum number of interests a person can have.
        max_interests (int): The maximum number of interests a person can have.
        bimodal_discount (int): The discount to apply to 50% of people's points total.

        Returns:
        DinnerParty: A new DinnerParty object with randomly generated people and interests.

        Raises:
        ValueError: If there are not enough names or interests in the respective files.
        """
        # Read names from the file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        names_file = os.path.join(script_dir, 'names.txt')
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f]

        # Read interests from the file
        interests_file = os.path.join(script_dir, 'interests.txt')
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

        # Calculate average points per person
        avg_points = total_points // num_people

        # Randomly assign points to each person, ensuring at least 1 point per person
        points_per_person = [max(1, random.randint(avg_points - points_spread, avg_points + points_spread)) for _ in range(num_people)]
        
        # Apply bimodal discount to 50% of people
        if bimodal_discount > 0:
            discounted_indices = random.sample(range(num_people), num_people // 2)
            for idx in discounted_indices:
                points_per_person[idx] = max(1, points_per_person[idx] - bimodal_discount)

        people = [Person.random_person(name, selected_interests, points, min_interests, max_interests) 
                  for name, points in zip(selected_names, points_per_person)]
        task_description = f"Select {set_size} people for a dinner party that will have the most engaging conversations."
        return cls(task_description, people, set_size)

    def to_prompt(self) -> str:
        """
        Generate a prompt string for the dinner party task.

        Returns:
        str: A string containing the task description, people and their interests, the question, and an explanation of the scoring method.
        """
        prompt = f"{self.task_description}\n\nPeople and their interests:\n"
        for i, person in enumerate(self.people, 1):
            interests_str = ", ".join([f"{interest} (level {level})" for interest, level in person.interests.items()])
            prompt += f"{i}. {person.name}: {interests_str}\n"
        prompt += f"\nPlease choose {self.set_size} people that would create the most engaging dinner party."
        prompt += "\n\nScoring Explanation:\n"
        prompt += "The dinner party is scored based on the interests of the selected people. "
        prompt += "The scoring process works as follows:\n"
        prompt += "1. All interests of the selected people are collected.\n"
        prompt += "2. Interests are sorted by: number of people sharing the interest (descending), "
        prompt += "sum of interest levels (descending), and alphabetically.\n"
        prompt += "3. The top 3 interests are selected.\n"
        prompt += "4. The final score is the sum of all interest levels for these top 3 interests.\n"
        prompt += "Your goal is to maximize this score by selecting a diverse group with strong, shared interests.\n"
        # prompt += f"\nYour score to beat is: {self.target_score}."
        # prompt += f"\nI don't want you to think before answering, just answer in the following format:"
        # prompt += f"\n\nAnswer with \"Answer: <person1>, <person2>, ...\"."
        return prompt

    def get_random_set(self) -> List[str]:
        """
        Return a random set of people for the dinner party.

        Returns:
        List[str]: A list of randomly selected people's names.
        """
        return random.sample([person.name for person in self.people], self.set_size)

    @classmethod
    def from_dict(cls, data: Dict):
        """
        Create a DinnerParty instance from a dictionary.

        Args:
        data (Dict): A dictionary containing the DinnerParty data.

        Returns:
        DinnerParty: A new DinnerParty instance.
        """
        people = [Person(name=p['name'], interests=p['interests']) for p in data['people']]
        dinner_party = cls(
            task_description=data['task_description'],
            people=people,
            set_size=data['set_size']
        )
        
        # Set additional attributes if they exist in the data
        if 'stored_scores' in data:
            dinner_party.stored_scores = data['stored_scores']
        if 'target_score' in data:
            dinner_party.target_score = data['target_score']
        
        # If parameters are provided, store them as an attribute
        if 'parameters' in data:
            dinner_party.parameters = data['parameters']
        
        return dinner_party


