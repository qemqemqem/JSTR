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
from generation.tasks.dinner_party.dinner_party import Person

class InterestSelection(ABC):
    @abstractmethod
    def select_interests(self, people: List[Person]) -> List[str]:
        pass
    
    def __str__(self) -> str:
        return self.__class__.__name__

class TopInterestSelection(InterestSelection):
    """Selects each person's highest-value interest"""
    def select_interests(self, people: List[Person]) -> List[str]:
        """Returns a list of the highest-value interest for each person"""
        result = []
        for person in people:
            if person.interests:
                # Get interest with highest value, breaking ties alphabetically
                top_interest = max(person.interests.items(), 
                                 key=lambda x: (x[1], -ord(x[0][0])))
                result.append(top_interest[0])
        return result

class ScoringRule(ABC):
    def __init__(self, complexity_rating: int):
        self.complexity_rating = complexity_rating
    
    @abstractmethod
    def score_round(self, people: List[Person]) -> Dict[str, float]:
        """Returns a dict mapping person names to their scores"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Returns a human-readable description of how the rule works"""
        pass

    def __str__(self) -> str:
        return f"CR{self.complexity_rating}: {self.get_description()}"

class TopInterestRule(ScoringRule):
    """CR1 rule: Each guest gets their top interest value"""
    
    def get_description(self) -> str:
        return "Score each guest's highest-value interest"
    def __init__(self):
        super().__init__(complexity_rating=1)
        self.selector = TopInterestSelection()
    
    def score_round(self, people: List[Person]) -> Dict[str, float]:
        scores = {}
        for person in people:
            if person.interests:
                # Get highest value interest
                top_value = max(person.interests.values())
                scores[person.name] = top_value
            else:
                scores[person.name] = 0
        return scores

class SharedInterestRule(ScoringRule):
    """CR2 rule: Points for interests shared between guests"""
    
    def get_description(self) -> str:
        return "Award points for interests that are shared between multiple guests"
    def __init__(self):
        super().__init__(complexity_rating=2)
    
    def score_round(self, people: List[Person]) -> Dict[str, float]:
        scores = {p.name: 0 for p in people}
        # Count how many people share each interest
        interest_counts = {}
        for person in people:
            for interest in person.interests:
                interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        # Award points for shared interests
        for person in people:
            for interest in person.interests:
                if interest_counts[interest] > 1:
                    scores[person.name] += person.interests[interest]
        return scores

class MostCommonInterestRule(ScoringRule):
    """CR3 rule: Points for the most common interest among guests"""
    
    def get_description(self) -> str:
        return "Double points for the most commonly shared interest among guests"
    def __init__(self):
        super().__init__(complexity_rating=3)
    
    def score_round(self, people: List[Person]) -> Dict[str, float]:
        scores = {p.name: 0 for p in people}
        # Find the most common interest
        interest_counts = {}
        for person in people:
            for interest in person.interests:
                interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        if not interest_counts:
            return scores
            
        most_common = max(interest_counts.items(), key=lambda x: (x[1], x[0]))[0]
        
        # Award points for the most common interest
        for person in people:
            if most_common in person.interests:
                scores[person.name] = person.interests[most_common] * 2
        return scores

@dataclass
class GameScoring:
    target_complexity: int
    rules: List[ScoringRule]

    def __str__(self) -> str:
        header = f"GameScoring (Total Complexity: CR{self.target_complexity})"
        rules_str = "\n".join(f"Round {i+1}: {str(rule)}" 
                             for i, rule in enumerate(self.rules))
        return f"{header}\n{rules_str}"
    
    def __post_init__(self):
        # Validate that rules sum to target complexity
        total_complexity = sum(rule.complexity_rating for rule in self.rules)
        if total_complexity != self.target_complexity:
            # TODO This is an error
            print(
                f"Rules complexity ({total_complexity}) "
                f"doesn't match target ({self.target_complexity})"
            )
        self.current_round = 0
        self.scores: Dict[str, float] = {}
    
    def score_round(self, people: List[Person]) -> Dict[str, float]:
        if self.current_round >= len(self.rules):
            raise ValueError("No more rounds available")
            
        # Get scores for this round
        round_scores = self.rules[self.current_round].score_round(people)
        
        # Update cumulative scores
        for name, score in round_scores.items():
            if name not in self.scores:
                self.scores[name] = 0
            self.scores[name] += score
        
        self.current_round += 1
        return round_scores
    
    def get_final_scores(self) -> Dict[str, float]:
        return self.scores.copy()

def random_scoring_rules(points: int):
    """Generate random scoring rules totaling the given complexity points"""
    available_rules = {
        1: TopInterestRule,
        2: SharedInterestRule,
        3: MostCommonInterestRule
    }
    
    rules = []
    remaining_points = points
    
    # Keep adding rules until we reach the target points
    while remaining_points > 0:
        # Get possible rules we could add
        possible_rules = [cr for cr, rule in available_rules.items() 
                         if cr <= remaining_points]
        
        if not possible_rules:
            break
            
        # Choose a rule
        chosen_cr = random.choice(possible_rules)
        rules.append(available_rules[chosen_cr]())
        remaining_points -= chosen_cr
    
    return GameScoring(target_complexity=points, rules=rules)

def main():
    points = random.randint(0, 10)
    print(f"Generating rules with Points: {points}")

    random_rules = random_scoring_rules(points)

    print("Rules:")
    print(random_rules)


if __name__ == "__main__":
    main()
