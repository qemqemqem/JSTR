"""
A utility for generating random scoring rules for a dinner party game.

In this game, the player must choose 5 dinner party guests from a list of 10. Each guest has some set of interests, like a level 4 interest in cooking, or a level 7 interest in gardening.

The scoring for this game can be randomized, and this file contains utilities for generating random scoring rules.

Typically, scoring rules are applied in multiple rounds of scoring. Different scoring rules can be more or less complex.

Each rule has some selection mechanism for choosing which interests are involved in the scoring. A simple rule might be to always choose sports and cooking, while a more complex rule might choose the top 3 interests of each guest.

Each rule has some scoring mechanism for determining how many points a guest gets. A simple rule might be to add up the interest values for the chosen interest, while a more complex rule might give 1 point for each interest, plus 1 point for each interest that is shared with the host.

Here are some examples of scoring rules:

- (CR1) Each guest gets their top interest value.
- (CR1) Each guest gets their value in cooking interest.
- (CR2) Each guest gets the sum of their top 3 interests.
- (CR2) Each guest gets their second-highest interest value.
- (CR3) The most common interest is chosen among all guests, and each guest gets their value in that interest.
- (CR3) The largest interest value is chosen among all guests, and each guest gets their value in that interest.
- (CR4) The host is chosen as the alphabetically lowest guest, and each guest gets 2 points for each interest they share with the host.
- (CR4) The most common interest is chosen among all guests, excluding interests which have been chosen in previous rounds, and each guest gets their value in that interest. (Round 2 and later only)
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from generation.tasks.dinner_party.dinner_party import Person, DinnerParty


class ScoringRule(ABC):
    def __init__(self, dinner_party: DinnerParty):
        pass
    
    @abstractmethod
    def score_round(self, people: List[Person]) -> tuple[Dict[str, float], List[str]]:
        """Returns a tuple of (scores dict mapping person names to their scores, list of interests discussed)"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Returns a human-readable description of how the rule works"""
        pass

    @classmethod
    @abstractmethod
    def get_cr(cls) -> int:
        pass

    def __str__(self) -> str:
        return f"CR{self.get_cr()}: {self.get_description()}"

class TopInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
    
    def score_round(self, people: List[Person]) -> tuple[Dict[str, float], List[str]]:
        scores = {}
        interests_used = []
        for person in people:
            # Get the highest value interest, breaking ties alphabetically
            top_interest = max(person.interests.items(), key=lambda x: (x[1], -ord(x[0][0])))
            scores[person.name] = top_interest[1]
            interests_used.append(top_interest[0])
        return scores, list(set(interests_used))

    @classmethod
    def get_cr(cls) -> int:
        return 1
    
    def get_description(self) -> str:
        return "Each person is awarded their top interest value in points"


class SingleInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)
        self.interest = random.choice(dinner_party.all_interests)

    def score_round(self, people: List[Person]) -> tuple[Dict[str, float], List[str]]:
        scores = {}
        for person in people:
            # Award points for the specific interest if they have it
            scores[person.name] = person.interests.get(self.interest, 0)
        return scores, [self.interest]

    @classmethod
    def get_cr(cls) -> int:
        return 1

    def get_description(self) -> str:
        return f"Award each person their value in {self.interest} in points."


class MostCommonInterestRule(ScoringRule):
    def __init__(self, dinner_party: DinnerParty):
        super().__init__(dinner_party)

    def score_round(self, people: List[Person]) -> tuple[Dict[str, float], List[str]]:
        # Count how many people have each interest
        interest_counts = {}
        for person in people:
            for interest in person.interests:
                interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        # Find the most common interest (breaking ties alphabetically)
        most_common = max(interest_counts.items(), key=lambda x: (x[1], -ord(x[0][0])))
        most_common_interest = most_common[0]
        
        # Award double points for the most common interest
        scores = {}
        for person in people:
            scores[person.name] = 2 * person.interests.get(most_common_interest, 0)
        return scores, [most_common_interest]

    @classmethod
    def get_cr(cls) -> int:
        return 3

    def get_description(self) -> str:
        return "First, find the most commonly shared interest by number of people with the interest (breaking ties alphabetically). Then, award each person their value in that interest in points."


@dataclass
class GameScoring:
    target_complexity: int
    rules: List[ScoringRule]

    def __str__(self) -> str:
        header = f"GameScoring (Total Complexity: CR{sum(rule.get_cr() for rule in self.rules)})"
        rounds = []
        for i, rule in enumerate(self.rules, 1):
            assert isinstance(rule, ScoringRule), f"Got {rule}, a {rule.__class__.__name__}"  # For IDE type hinting
            round_desc = f"Round {i}: CR{rule.get_cr()}-{rule.__class__.__name__}: {rule.get_description()}"
            rounds.append(round_desc)
        return f"{header}\n" + "\n".join(rounds)
    
    def __post_init__(self):
        # Validate that rules sum to target complexity
        total_complexity = sum(rule.get_cr() for rule in self.rules)
        if total_complexity != self.target_complexity:
            # TODO This is an error
            print(
                f"Rules complexity ({total_complexity}) "
                f"doesn't match target ({self.target_complexity})"
            )
        self.current_round = 0
        self.scores: Dict[str, float] = {}
    
    def score_all_rounds(self, people: List[Person]) -> Dict[str, float]:
        """Score all rounds and return final scores"""
        discussed_interests = []
        
        print("\nScoring all rounds:")
        for round_num, rule in enumerate(self.rules, 1):
            print(f"\nRound {round_num}:")
            # Get scores and interests for this round
            round_scores, round_interests = rule.score_round(people)
            
            # Print what happened this round
            print(f"Discussed interests: {', '.join(round_interests)}")
            print("Scores this round:")
            for name, score in round_scores.items():
                print(f"  {name}: {score}")
            
            # Update cumulative scores
            for name, score in round_scores.items():
                if name not in self.scores:
                    self.scores[name] = 0
                self.scores[name] += score
            
            # Track discussed interests
            discussed_interests.extend(round_interests)
        
        print("\nFinal cumulative scores:")
        for name, score in sorted(self.scores.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {name}: {score}")
        print(f"\nAll interests discussed: {', '.join(sorted(set(discussed_interests)))}")
        
        return self.scores.copy()
    
    def get_final_scores(self) -> Dict[str, float]:
        return self.scores.copy()

def random_scoring_rules(points: int, dinner_party: DinnerParty):
    """Generate random scoring rules totaling the given complexity points"""
    available_rules = [
        TopInterestRule,
        MostCommonInterestRule,
        SingleInterestRule,
    ]
    
    rules = []
    remaining_points = points
    
    # Keep adding rules until we reach the target points
    while remaining_points > 0:
        # Get possible rules we could add
        possible_rules = [rule for rule in available_rules if rule.get_cr() <= remaining_points]
        
        if not possible_rules:
            break
            
        # Choose a rule
        chosen_rule = random.choice(possible_rules)(dinner_party)
        rules.append(chosen_rule)
        remaining_points -= chosen_rule.get_cr()
    
    return GameScoring(target_complexity=points, rules=rules)

def main():
    dinner_party = DinnerParty.random_dinner_party(num_people=10, num_interests=6, set_size=5, points_spread=0, min_interests=2, max_interests=4, avg_points=15)

    points = 6  # random.randint(3, 10)
    print(f"Generating rules with Points: {points}")

    random_rules = random_scoring_rules(points, dinner_party)

    print("Rules:")
    print(random_rules)


if __name__ == "__main__":
    main()
