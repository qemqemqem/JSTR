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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from generation.tasks.dinner_party.dinner_party import Person

class InterestSelection(ABC):
    @abstractmethod
    def select_interests(self, people: List[Person]) -> List[str]:
        pass

class TopInterestSelection(InterestSelection):
    """Selects each person's highest-value interest"""
    def select_interests(self, people: List[Person]) -> List[str]:
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

class TopInterestRule(ScoringRule):
    """CR1 rule: Each guest gets their top interest value"""
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

@dataclass
class GameScoring:
    target_complexity: int
    rules: List[ScoringRule]
    
    def __post_init__(self):
        # Validate that rules sum to target complexity
        total_complexity = sum(rule.complexity_rating for rule in self.rules)
        if total_complexity != self.target_complexity:
            raise ValueError(
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
    rules = [TopInterestRule()]  # Start with simplest rule for now
    return GameScoring(target_complexity=points, rules=rules)

def main():
    points = random.randint(0, 10)
    print(f"Generating rules with Points: {points}")

    random_rules = random_scoring_rules(points)


if __name__ == "__main__":
    main()
